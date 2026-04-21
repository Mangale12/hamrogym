from __future__ import annotations

from calendar import monthrange
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Iterable

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from Nepanest.account.models import JournalEntry, JournalEntrySide, JournalEntryStatus, JournalLine, VoucherType
from Nepanest.account.services.journal_service import post_journal_entry, prepare_journal_entry_for_save, synchronize_journal_entry

from ..models import Asset, AssetCategory, AssetDepreciationRegister


ZERO = Decimal("0.00")


def _to_decimal(value) -> Decimal:
    if value in (None, ""):
        return ZERO
    return Decimal(str(value)).quantize(Decimal("0.01"))


def _quantize(value: Decimal | None) -> Decimal:
    return (value or ZERO).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _month_start(value: date) -> date:
    return value.replace(day=1)


def _month_end(value: date) -> date:
    return value.replace(day=monthrange(value.year, value.month)[1])


def normalize_schedule_month(value: date) -> date:
    return _month_start(value)


def parse_schedule_month_value(value) -> date:
    if isinstance(value, date):
        return normalize_schedule_month(value)

    raw = str(value or "").strip()
    if not raw:
        raise ValidationError({"schedule_month": "Schedule month is required."})

    if len(raw) == 7:
        raw = f"{raw}-01"

    try:
        parsed = date.fromisoformat(raw)
    except ValueError as exc:
        raise ValidationError({"schedule_month": "Enter a valid schedule month."}) from exc

    return normalize_schedule_month(parsed)


def _add_months(value: date, months: int) -> date:
    month_index = (value.month - 1) + months
    year = value.year + (month_index // 12)
    month = (month_index % 12) + 1
    return date(year, month, 1)


def _resolve_category(asset: Asset) -> AssetCategory | None:
    if asset.category_id:
        return asset.category
    if asset.asset_type_id and asset.asset_type and asset.asset_type.category_id:
        return asset.asset_type.category
    return None


def _resolve_profile(asset: Asset) -> Dict[str, object]:
    category = _resolve_category(asset)
    asset_type = asset.asset_type
    depreciation_applicable = bool(
        (category and category.depreciation_applicable)
        or (asset_type and asset_type.depreciation_applicable)
    )
    useful_life_months = asset.use_full_life_months or getattr(category, "default_useful_life_months", None)
    purchase_date = asset.purchase_date
    depreciation_start_date = asset.depreciation_start_date or purchase_date
    purchase_cost = _to_decimal(asset.purchase_cost)
    salvage_value = _to_decimal(asset.salvage_value)

    return {
        "category": category,
        "depreciation_applicable": depreciation_applicable,
        "useful_life_months": useful_life_months,
        "depreciation_start_date": depreciation_start_date,
        "purchase_cost": purchase_cost,
        "salvage_value": salvage_value,
        "fixed_asset_account": getattr(category, "fixed_asset_account", None),
        "depreciation_expense_account": getattr(category, "depreciation_expense_account", None),
        "accumulated_depreciation_account": getattr(category, "accumulated_depreciation_account", None),
        "method": getattr(category, "depreciation_method", AssetCategory.DEPRECIATION_METHOD_STRAIGHT_LINE)
        if category
        else AssetCategory.DEPRECIATION_METHOD_STRAIGHT_LINE,
    }


def validate_asset_for_depreciation(asset: Asset) -> Dict[str, object]:
    profile = _resolve_profile(asset)
    errors = {}

    if not asset.is_active:
        errors["asset"] = "Inactive assets cannot generate depreciation schedules."
    if not profile["depreciation_applicable"]:
        errors["asset"] = "This asset is not marked as depreciation applicable."
    if not profile["depreciation_start_date"]:
        errors["depreciation_start_date"] = "Purchase date or depreciation start date is required."
    if profile["purchase_cost"] <= ZERO:
        errors["purchase_cost"] = "Purchase cost must be greater than zero."
    if profile["salvage_value"] < ZERO:
        errors["salvage_value"] = "Salvage value cannot be negative."
    if profile["salvage_value"] > profile["purchase_cost"]:
        errors["salvage_value"] = "Salvage value cannot exceed purchase cost."
    if not profile["useful_life_months"] or int(profile["useful_life_months"]) <= 0:
        errors["useful_life_months"] = "Useful life months is required and must be greater than zero."
    if not profile["fixed_asset_account"]:
        errors["fixed_asset_account"] = "Asset category must define a fixed asset ledger."
    if not profile["depreciation_expense_account"]:
        errors["depreciation_expense_account"] = "Asset category must define a depreciation expense ledger."
    if not profile["accumulated_depreciation_account"]:
        errors["accumulated_depreciation_account"] = "Asset category must define an accumulated depreciation ledger."
    if profile["method"] != AssetCategory.DEPRECIATION_METHOD_STRAIGHT_LINE:
        errors["depreciation_method"] = "Only straight-line depreciation is supported right now."

    if errors:
        raise ValidationError(errors)

    return profile


def _flatten_validation_error(exc: ValidationError) -> str:
    if hasattr(exc, "message_dict"):
        parts = []
        for field_messages in exc.message_dict.values():
            if isinstance(field_messages, (list, tuple)):
                parts.extend(str(item) for item in field_messages if item)
            elif field_messages:
                parts.append(str(field_messages))
        return " ".join(parts).strip()

    messages = exc.messages if hasattr(exc, "messages") else [str(exc)]
    return " ".join(str(item) for item in messages if item).strip()


def validate_schedule_month_for_fiscal_year(schedule_month: date, fiscal_year) -> date:
    normalized_month = normalize_schedule_month(schedule_month)
    month_end = _month_end(normalized_month)

    if fiscal_year and (month_end < fiscal_year.start_date or normalized_month > fiscal_year.end_date):
        raise ValidationError(
            {
                "schedule_month": (
                    f"Selected month {normalized_month:%Y-%m} is outside fiscal year {fiscal_year.name} "
                    f"({fiscal_year.start_date} to {fiscal_year.end_date})."
                )
            }
        )

    return normalized_month


def generate_asset_depreciation_schedule(
    asset: Asset,
    *,
    organization=None,
    branch=None,
    fiscal_year=None,
    through_date: date | None = None,
) -> Dict[str, int]:
    profile = validate_asset_for_depreciation(asset)
    useful_life_months = int(profile["useful_life_months"])
    start_month = _month_start(profile["depreciation_start_date"])
    through_month = _month_start(through_date or (fiscal_year.end_date if fiscal_year else timezone.localdate()))
    purchase_cost = profile["purchase_cost"]
    salvage_value = profile["salvage_value"]
    depreciable_amount = _quantize(max(purchase_cost - salvage_value, ZERO))
    base_monthly = _quantize(depreciable_amount / Decimal(useful_life_months))

    existing_map = {
        entry.schedule_month: entry
        for entry in asset.depreciation_register_entries.filter(branch=branch).select_related("journal_entry")
    }

    created_count = 0
    updated_count = 0
    skipped_count = 0
    accumulated_before = ZERO

    with transaction.atomic():
        for month_index in range(useful_life_months):
            schedule_month = _add_months(start_month, month_index)
            if schedule_month > through_month:
                break

            period_start = _month_start(schedule_month)
            period_end = _month_end(schedule_month)
            if month_index == useful_life_months - 1:
                depreciation_amount = _quantize(depreciable_amount - accumulated_before)
            else:
                depreciation_amount = base_monthly

            opening_book_value = _quantize(purchase_cost - accumulated_before)
            closing_book_value = _quantize(opening_book_value - depreciation_amount)
            if closing_book_value < salvage_value:
                closing_book_value = _quantize(salvage_value)
                depreciation_amount = _quantize(opening_book_value - closing_book_value)

            defaults = {
                "organization": organization,
                "branch": branch,
                "fiscal_year": fiscal_year,
                "period_start": period_start,
                "period_end": period_end,
                "method": profile["method"],
                "life_month_index": month_index + 1,
                "useful_life_months": useful_life_months,
                "purchase_cost": purchase_cost,
                "salvage_value": salvage_value,
                "depreciable_amount": depreciable_amount,
                "depreciation_amount": depreciation_amount,
                "opening_book_value": opening_book_value,
                "closing_book_value": closing_book_value,
                "fixed_asset_account": profile["fixed_asset_account"],
                "depreciation_expense_account": profile["depreciation_expense_account"],
                "accumulated_depreciation_account": profile["accumulated_depreciation_account"],
                "remarks": f"Generated from asset depreciation schedule for {asset.name}.",
            }

            existing = existing_map.get(schedule_month)
            if existing:
                if existing.status == AssetDepreciationRegister.STATUS_POSTED:
                    depreciation_amount = _to_decimal(existing.depreciation_amount)
                    skipped_count += 1
                else:
                    for key, value in defaults.items():
                        setattr(existing, key, value)
                    existing.save()
                    updated_count += 1
            else:
                AssetDepreciationRegister.objects.create(
                    asset=asset,
                    schedule_month=schedule_month,
                    **defaults,
                )
                created_count += 1

            accumulated_before = _quantize(accumulated_before + depreciation_amount)

    return {
        "created": created_count,
        "updated": updated_count,
        "skipped": skipped_count,
    }


def generate_depreciation_schedule_for_assets(
    assets: Iterable[Asset],
    *,
    organization=None,
    branch=None,
    fiscal_year=None,
    through_date: date | None = None,
) -> Dict[str, int]:
    summary = {"assets": 0, "created": 0, "updated": 0, "skipped": 0}
    for asset in assets:
        result = generate_asset_depreciation_schedule(
            asset,
            organization=organization,
            branch=branch,
            fiscal_year=fiscal_year,
            through_date=through_date,
        )
        summary["assets"] += 1
        summary["created"] += result["created"]
        summary["updated"] += result["updated"]
        summary["skipped"] += result["skipped"]
    return summary


def generate_monthly_depreciation_schedule(
    *,
    schedule_month: date,
    organization=None,
    branch=None,
    fiscal_year=None,
) -> Dict[str, object]:
    normalized_month = validate_schedule_month_for_fiscal_year(schedule_month, fiscal_year)
    through_date = _month_end(normalized_month)
    month_label = normalized_month.strftime("%B %Y")

    assets = (
        Asset.objects.select_related("category", "asset_type", "asset_type__category")
        .filter(is_active=True)
        .filter(
            Q(category__depreciation_applicable=True)
            | Q(asset_type__depreciation_applicable=True)
        )
        .order_by("name", "id")
    )

    summary = {
        "month": normalized_month,
        "month_label": month_label,
        "assets_considered": 0,
        "assets_processed": 0,
        "not_due": 0,
        "created": 0,
        "updated": 0,
        "skipped": 0,
        "errors": [],
    }

    for asset in assets:
        summary["assets_considered"] += 1
        start_date = asset.depreciation_start_date or asset.purchase_date
        if start_date and _month_start(start_date) > normalized_month:
            summary["not_due"] += 1
            continue

        try:
            result = generate_asset_depreciation_schedule(
                asset,
                organization=organization,
                branch=branch,
                fiscal_year=fiscal_year,
                through_date=through_date,
            )
        except ValidationError as exc:
            summary["errors"].append(
                f"{asset.name}: {_flatten_validation_error(exc) or 'Validation failed.'}"
            )
            continue

        summary["assets_processed"] += 1
        summary["created"] += result["created"]
        summary["updated"] += result["updated"]
        summary["skipped"] += result["skipped"]

    summary["error_count"] = len(summary["errors"])
    return summary


def _get_or_create_depreciation_voucher_type() -> VoucherType:
    voucher_type, _created = VoucherType.objects.get_or_create(
        code="DEPR",
        defaults={
            "name": "Depreciation Journal",
            "category": "journal",
            "nature": "both",
            "affects_cash": False,
            "affects_bank": False,
            "auto_numbering": True,
            "prefix": "DEPR-",
            "is_system_generated": True,
            "is_active": True,
            "description": "System generated voucher type for asset depreciation.",
        },
    )
    return voucher_type


@transaction.atomic
def post_depreciation_entry(register_entry: AssetDepreciationRegister, *, user=None) -> AssetDepreciationRegister:
    entry = (
        AssetDepreciationRegister.objects.select_for_update()
        .select_related(
            "asset",
            "branch",
            "fiscal_year",
            "organization",
            "depreciation_expense_account",
            "accumulated_depreciation_account",
            "journal_entry",
        )
        .get(pk=register_entry.pk)
    )

    if entry.status == AssetDepreciationRegister.STATUS_POSTED:
        raise ValidationError("This depreciation entry has already been posted.")

    if entry.depreciation_amount <= ZERO:
        raise ValidationError("Depreciation amount must be greater than zero before posting.")

    voucher_type = _get_or_create_depreciation_voucher_type()
    organization = entry.organization or (entry.branch.organization if entry.branch_id else None)
    journal_entry = JournalEntry(
        organization=organization,
        branch=entry.branch,
        fiscal_year=entry.fiscal_year,
        date=entry.period_end,
        voucher_type=voucher_type,
        reference_no=f"DEP-{entry.asset.code or entry.asset_id}-{entry.schedule_month:%Y%m}",
        narration=f"Depreciation for {entry.asset.name} - {entry.schedule_month:%B %Y}",
        remarks=f"Auto-generated from depreciation register entry #{entry.pk}.",
        status=JournalEntryStatus.DRAFT,
    )
    prepare_journal_entry_for_save(journal_entry)
    journal_entry.save()

    JournalLine.objects.create(
        journal_entry=journal_entry,
        account=entry.depreciation_expense_account,
        description=f"Depreciation expense for {entry.asset.name}",
        entry_side=JournalEntrySide.DEBIT,
        amount=entry.depreciation_amount,
        sort_order=1,
    )
    JournalLine.objects.create(
        journal_entry=journal_entry,
        account=entry.accumulated_depreciation_account,
        description=f"Accumulated depreciation for {entry.asset.name}",
        entry_side=JournalEntrySide.CREDIT,
        amount=entry.depreciation_amount,
        sort_order=2,
    )

    synchronize_journal_entry(journal_entry)
    posted_entry = post_journal_entry(journal_entry, user=user)

    entry.journal_entry = posted_entry
    entry.status = AssetDepreciationRegister.STATUS_POSTED
    entry.posted_at = timezone.now()
    entry.posted_by = user
    entry.save(update_fields=["journal_entry", "status", "posted_at", "posted_by", "updated_at"])
    return entry


def post_monthly_depreciation_entries(
    *,
    schedule_month: date,
    branch=None,
    fiscal_year=None,
    user=None,
) -> Dict[str, object]:
    normalized_month = validate_schedule_month_for_fiscal_year(schedule_month, fiscal_year)
    month_entries = AssetDepreciationRegister.objects.select_related(
        "asset",
        "journal_entry",
        "branch",
        "fiscal_year",
    ).filter(
        schedule_month=normalized_month,
    )

    if branch is not None:
        month_entries = month_entries.filter(branch=branch)
    if fiscal_year is not None:
        month_entries = month_entries.filter(fiscal_year=fiscal_year)

    summary = {
        "month": normalized_month,
        "month_label": normalized_month.strftime("%B %Y"),
        "total_entries": month_entries.count(),
        "already_posted": month_entries.filter(status=AssetDepreciationRegister.STATUS_POSTED).count(),
        "unposted_entries": month_entries.filter(status=AssetDepreciationRegister.STATUS_UNPOSTED).count(),
        "posted": 0,
        "total_amount": ZERO,
        "errors": [],
    }

    for entry in month_entries.filter(status=AssetDepreciationRegister.STATUS_UNPOSTED).order_by("asset__name", "id"):
        try:
            posted_entry = post_depreciation_entry(entry, user=user)
        except ValidationError as exc:
            summary["errors"].append(
                f"{entry.asset.name}: {_flatten_validation_error(exc) or 'Posting failed.'}"
            )
            continue

        summary["posted"] += 1
        summary["total_amount"] = _quantize(summary["total_amount"] + _to_decimal(posted_entry.depreciation_amount))

    summary["error_count"] = len(summary["errors"])
    summary["remaining_unposted"] = max(summary["unposted_entries"] - summary["posted"], 0)
    return summary
