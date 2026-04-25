from decimal import Decimal

from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from nepanest.modules.payroll.models import (
    AttendancePayrollSummary,
    EmployeeSalaryAssignment,
    EmployeeTaxDeclaration,
    LeavePayrollImpact,
    PayrollAdjustment,
    PayrollApproval,
    PayrollLock,
    PayrollLog,
    PayrollRun,
    PayrollRunComponent,
    PayrollRunEmployee,
    PayrollSetting,
    Payslip,
    ProvidentFund,
    SSFContribution,
    TaxSlab,
)
from nepanest.modules.human_resources.services.payroll_formula_engine import (
    FormulaEvaluationError,
    apply_rounding,
    evaluate_formula,
    to_decimal,
)
from nepanest.modules.human_resources.services.payroll_inputs import build_attendance_payroll_inputs, build_leave_payroll_inputs


def get_active_salary_assignments(*, payroll_run: PayrollRun):
    return (
        EmployeeSalaryAssignment.objects.filter(
            is_active=True,
            effective_from__lte=payroll_run.period_end,
        )
        .filter(Q(effective_to__isnull=True) | Q(effective_to__gte=payroll_run.period_start))
        .select_related("employee", "salary_structure")
        .prefetch_related(
            "component_overrides",
            "salary_structure__components__salary_component",
            "salary_structure__components__percentage_of_component",
        )
        .order_by("employee__employee_id", "-effective_from", "-id")
    )


def _assignment_overrides(assignment: EmployeeSalaryAssignment):
    return {
        item.salary_component_id: item
        for item in assignment.component_overrides.all()
    }


def _structure_components(assignment: EmployeeSalaryAssignment):
    return list(
        assignment.salary_structure.components.select_related(
            "salary_component",
            "percentage_of_component",
        ).order_by("sequence", "id")
    )


def _component_amount(component, override, context):
    base_component = component.percentage_of_component
    expression = ""
    source_type = "structure"

    if override and override.override_formula:
        expression = override.override_formula
        source_type = "override"
    elif override and override.override_value is not None:
        return apply_rounding(override.override_value, component.rounding_rule), source_type
    elif component.formula_expression:
        expression = component.formula_expression
    elif component.salary_component.formula_expression:
        expression = component.salary_component.formula_expression

    if expression:
        return apply_rounding(evaluate_formula(expression, context), component.rounding_rule), source_type

    if base_component and component.default_value is not None:
        base_amount = to_decimal(context.get(base_component.code, Decimal("0.00")))
        percentage_value = to_decimal(component.default_value)
        return apply_rounding((base_amount * percentage_value) / Decimal("100"), component.rounding_rule), source_type

    return apply_rounding(component.default_value or Decimal("0.00"), component.rounding_rule), source_type


def _build_component_rows(assignment: EmployeeSalaryAssignment):
    component_rows = []
    context = {
        "GROSS": to_decimal(assignment.gross_salary),
        "ANNUAL_CTC": to_decimal(assignment.annual_ctc),
    }
    overrides = _assignment_overrides(assignment)

    for structure_component in _structure_components(assignment):
        override = overrides.get(structure_component.salary_component_id)
        amount, source_type = _component_amount(structure_component, override, context)
        if structure_component.min_value is not None and amount < structure_component.min_value:
            amount = to_decimal(structure_component.min_value)
        if structure_component.max_value is not None and amount > structure_component.max_value:
            amount = to_decimal(structure_component.max_value)

        context[structure_component.salary_component.code] = amount
        component_rows.append(
            {
                "salary_component": structure_component.salary_component,
                "source_type": source_type,
                "sequence": structure_component.sequence,
                "amount": amount,
                "component_type": structure_component.salary_component.component_type,
                "tax_treatment": structure_component.salary_component.tax_treatment,
                "calculation_trace": {
                    "component_code": structure_component.salary_component.code,
                    "formula_expression": override.override_formula if override and override.override_formula else (
                        structure_component.formula_expression or structure_component.salary_component.formula_expression or ""
                    ),
                    "default_value": str(structure_component.default_value or ""),
                    "percentage_of_component": structure_component.percentage_of_component.code if structure_component.percentage_of_component else "",
                },
            }
        )

    return component_rows


def _append_leave_and_adjustment_rows(*, payroll_run: PayrollRun, assignment: EmployeeSalaryAssignment, component_rows):
    leave_impacts = LeavePayrollImpact.objects.filter(
        payroll_run=payroll_run,
        employee=assignment.employee,
    ).select_related("leave_type")

    for impact in leave_impacts:
        if impact.deduction_amount > 0:
            component_rows.append(
                {
                    "salary_component": None,
                    "source_type": "leave",
                    "sequence": 900,
                    "amount": impact.deduction_amount,
                    "component_type": "deduction",
                    "tax_treatment": "non_taxable",
                    "calculation_trace": {
                        "days": str(impact.days),
                        "is_paid": impact.is_paid,
                        "leave_request_id": impact.leave_request_id,
                        "leave_type": impact.leave_type.name,
                    },
                }
            )

    adjustments = PayrollAdjustment.objects.filter(
        payroll_run=payroll_run,
        employee=assignment.employee,
    ).select_related("salary_component")
    for adjustment in adjustments:
        component = adjustment.salary_component
        component_type = component.component_type if component else (
            "deduction" if adjustment.adjustment_type == "deduction" else "earning"
        )
        tax_treatment = component.tax_treatment if component else "non_taxable"
        component_rows.append(
            {
                "salary_component": component,
                "source_type": "adjustment",
                "sequence": component.sequence if component else 950,
                "amount": adjustment.amount,
                "component_type": component_type,
                "tax_treatment": tax_treatment,
                "calculation_trace": {
                    "adjustment_type": adjustment.adjustment_type,
                    "reason": adjustment.reason,
                    "adjustment_id": adjustment.id,
                },
            }
        )

    return component_rows


def _append_overtime_rows(*, payroll_run: PayrollRun, assignment: EmployeeSalaryAssignment, component_rows):
    attendance_summary = AttendancePayrollSummary.objects.filter(
        payroll_run=payroll_run,
        employee=assignment.employee,
    ).first()
    payroll_setting = _get_payroll_setting(payroll_run)
    overtime_component = payroll_setting.overtime_earning_component if payroll_setting else None

    if not attendance_summary or not payroll_setting or not overtime_component:
        return component_rows

    overtime_hours = to_decimal(attendance_summary.overtime_hours)
    if overtime_hours <= 0:
        return component_rows

    working_days = Decimal(str((payroll_setting.default_working_days or 0) or 0))
    if working_days <= 0:
        working_days = Decimal("30.00")

    try:
        employee_payroll = assignment.employee.payroll
    except Exception:
        employee_payroll = None
    employee_ot_rate = to_decimal(getattr(employee_payroll, "overtime_rate", None))
    base_hourly_rate = (to_decimal(assignment.gross_salary) / working_days / Decimal("8.00")).quantize(Decimal("0.0001"))

    overtime_method = payroll_setting.overtime_calculation_method
    if overtime_method == "fixed_rate":
        overtime_rate = employee_ot_rate
    elif overtime_method == "multiplier":
        multiplier = employee_ot_rate if employee_ot_rate > 0 else Decimal("1.50")
        overtime_rate = (base_hourly_rate * multiplier).quantize(Decimal("0.0001"))
    else:
        overtime_rate = employee_ot_rate if employee_ot_rate > 0 else base_hourly_rate

    if overtime_rate <= 0:
        return component_rows

    overtime_amount = apply_rounding(
        overtime_hours * overtime_rate,
        payroll_setting.rounding_method if payroll_setting else "round_2",
    )
    if overtime_amount <= 0:
        return component_rows

    component_rows.append(
        {
            "salary_component": overtime_component,
            "source_type": "overtime",
            "sequence": overtime_component.sequence,
            "quantity": overtime_hours,
            "rate": overtime_rate,
            "amount": overtime_amount,
            "component_type": overtime_component.component_type,
            "tax_treatment": overtime_component.tax_treatment,
            "calculation_trace": {
                "overtime_hours": str(overtime_hours),
                "overtime_rate": str(overtime_rate),
                "overtime_method": overtime_method,
                "base_hourly_rate": str(base_hourly_rate),
                "employee_overtime_rate": str(employee_ot_rate),
                "attendance_summary_id": attendance_summary.id,
            },
        }
    )

    return component_rows


def _apply_attendance_proration(*, payroll_run: PayrollRun, assignment: EmployeeSalaryAssignment, component_rows):
    attendance_summary = AttendancePayrollSummary.objects.filter(
        payroll_run=payroll_run,
        employee=assignment.employee,
    ).first()
    payroll_setting = _get_payroll_setting(payroll_run)

    if not attendance_summary:
        return component_rows, None

    working_days = Decimal(str((payroll_setting.default_working_days if payroll_setting else 0) or 0))
    if working_days <= 0:
        working_days = Decimal("30.00")

    payable_days = to_decimal(attendance_summary.payable_days)
    if payable_days < 0:
        payable_days = Decimal("0.00")
    if payable_days > working_days:
        payable_days = working_days

    proration_factor = (payable_days / working_days).quantize(Decimal("0.0001"))
    if proration_factor >= Decimal("1.0000"):
        return component_rows, {
            "attendance_summary_id": attendance_summary.id,
            "working_days": str(working_days),
            "payable_days": str(payable_days),
            "proration_factor": str(proration_factor),
            "prorated_components": [],
        }

    prorated_components = []
    for row in component_rows:
        if row.get("component_type") != "earning":
            continue
        if row.get("source_type") not in {"structure", "override"}:
            continue

        original_amount = to_decimal(row["amount"])
        prorated_amount = original_amount
        salary_component = row.get("salary_component")
        if salary_component and salary_component.affects_net:
            prorated_amount = original_amount * proration_factor
            prorated_amount = apply_rounding(
                prorated_amount,
                payroll_setting.rounding_method if payroll_setting else "round_2",
            )
            row["amount"] = prorated_amount

        if prorated_amount != original_amount:
            prorated_components.append(
                {
                    "component_code": salary_component.code if salary_component else "",
                    "original_amount": str(original_amount),
                    "prorated_amount": str(prorated_amount),
                }
            )

    return component_rows, {
        "attendance_summary_id": attendance_summary.id,
        "working_days": str(working_days),
        "payable_days": str(payable_days),
        "proration_factor": str(proration_factor),
        "prorated_components": prorated_components,
        "absent_days": str(attendance_summary.absent_days),
        "half_days": str(attendance_summary.half_days),
        "leave_days": str(attendance_summary.leave_days),
        "late_instances": attendance_summary.late_instances,
        "overtime_hours": str(attendance_summary.overtime_hours),
    }


def _calculate_totals(component_rows):
    gross_earnings = Decimal("0.00")
    total_deductions = Decimal("0.00")
    employer_contributions = Decimal("0.00")
    taxable_income = Decimal("0.00")

    for row in component_rows:
        component_type = row.get("component_type", "")
        tax_treatment = row.get("tax_treatment", "non_taxable")
        amount = to_decimal(row["amount"])
        if component_type == "earning":
            gross_earnings += amount
        elif component_type == "deduction":
            total_deductions += amount
        elif component_type == "employer_contribution":
            employer_contributions += amount

        if tax_treatment == "taxable" and component_type == "earning":
            taxable_income += amount

    net_salary = gross_earnings - total_deductions
    return {
        "gross_earnings": gross_earnings.quantize(Decimal("0.01")),
        "total_deductions": total_deductions.quantize(Decimal("0.01")),
        "employer_contributions": employer_contributions.quantize(Decimal("0.01")),
        "taxable_income": taxable_income.quantize(Decimal("0.01")),
        "income_tax": Decimal("0.00"),
        "net_salary": net_salary.quantize(Decimal("0.01")),
    }


def _payment_period_factor(payment_frequency: str) -> Decimal:
    return {
        "monthly": Decimal("12"),
        "biweekly": Decimal("26"),
        "weekly": Decimal("52"),
    }.get(payment_frequency or "monthly", Decimal("12"))


def _get_fiscal_year_for_run(payroll_run: PayrollRun):
    from nepanest.foundation.fiscal import FiscalYear

    if getattr(payroll_run, "fiscal_year_id", None):
        return payroll_run.fiscal_year

    return (
        FiscalYear.objects.filter(
            start_date__lte=payroll_run.period_end,
            end_date__gte=payroll_run.period_start,
        )
        .order_by("-start_date", "-id")
        .first()
    )


def _calculate_tax_from_slabs(annual_taxable_income: Decimal, slabs):
    annual_tax = Decimal("0.00")
    remaining_income = to_decimal(annual_taxable_income)

    for slab in slabs:
        lower = to_decimal(slab.min_income)
        upper = to_decimal(slab.max_income) if slab.max_income is not None else None
        if remaining_income <= lower:
            continue

        taxable_portion = (remaining_income - lower) if upper is None else min(remaining_income, upper) - lower
        if taxable_portion <= 0:
            continue
        annual_tax += (taxable_portion * to_decimal(slab.tax_rate)) / Decimal("100")
        if slab.rebate_amount:
            annual_tax -= to_decimal(slab.rebate_amount)

    return max(annual_tax, Decimal("0.00")).quantize(Decimal("0.01"))


def _get_payroll_setting(payroll_run: PayrollRun):
    scoped_settings = PayrollSetting.objects.filter(is_active=True)
    if payroll_run.organization_id:
        branch_setting = scoped_settings.filter(
            organization_id=payroll_run.organization_id,
            branch_id=payroll_run.branch_id,
        ).first()
        if branch_setting:
            return branch_setting

        org_setting = scoped_settings.filter(
            organization_id=payroll_run.organization_id,
            branch__isnull=True,
        ).first()
        if org_setting:
            return org_setting

    return scoped_settings.filter(organization__isnull=True, branch__isnull=True).first()


def _build_statutory_rows(*, payroll_run: PayrollRun, assignment: EmployeeSalaryAssignment, component_rows):
    effective_date = payroll_run.period_end
    statutory_rows = []
    payroll_setting = _get_payroll_setting(payroll_run)
    attendance_summary = AttendancePayrollSummary.objects.filter(
        payroll_run=payroll_run,
        employee=assignment.employee,
    ).first()
    working_days = Decimal(str((payroll_setting.default_working_days if payroll_setting else 0) or 0))
    if working_days <= 0:
        working_days = Decimal("30.00")
    payable_days = to_decimal(attendance_summary.payable_days) if attendance_summary else working_days
    if payable_days < 0:
        payable_days = Decimal("0.00")
    if payable_days > working_days:
        payable_days = working_days
    attendance_factor = (payable_days / working_days).quantize(Decimal("0.0001")) if working_days else Decimal("1.0000")
    statutory_base_amount = (to_decimal(assignment.gross_salary) * attendance_factor).quantize(Decimal("0.01"))

    provident_fund = (
        ProvidentFund.objects.filter(
            employee=assignment.employee,
            is_active=True,
            effective_from__lte=effective_date,
        )
        .filter(Q(effective_to__isnull=True) | Q(effective_to__gte=payroll_run.period_start))
        .order_by("-effective_from", "-id")
        .first()
    )
    if provident_fund:
        pf_employee_amount = (
            statutory_base_amount * to_decimal(provident_fund.employee_percent) / Decimal("100")
        ).quantize(Decimal("0.01"))
        pf_employer_amount = (
            statutory_base_amount * to_decimal(provident_fund.employer_percent) / Decimal("100")
        ).quantize(Decimal("0.01"))
        statutory_rows.extend(
            [
                {
                    "salary_component": payroll_setting.provident_fund_employee_component if payroll_setting else None,
                    "source_type": "statutory",
                    "sequence": 970,
                    "amount": pf_employee_amount,
                    "component_type": "deduction",
                    "tax_treatment": "non_taxable",
                    "calculation_trace": {
                        "statutory_type": "provident_fund_employee",
                        "percent": str(provident_fund.employee_percent),
                        "base_amount": str(statutory_base_amount),
                        "attendance_factor": str(attendance_factor),
                    },
                },
                {
                    "salary_component": payroll_setting.provident_fund_employer_component if payroll_setting else None,
                    "source_type": "statutory",
                    "sequence": 971,
                    "amount": pf_employer_amount,
                    "component_type": "employer_contribution",
                    "tax_treatment": "non_taxable",
                    "calculation_trace": {
                        "statutory_type": "provident_fund_employer",
                        "percent": str(provident_fund.employer_percent),
                        "base_amount": str(statutory_base_amount),
                        "attendance_factor": str(attendance_factor),
                    },
                },
            ]
        )

    ssf_contribution = (
        SSFContribution.objects.filter(
            employee=assignment.employee,
            is_active=True,
            effective_from__lte=effective_date,
        )
        .filter(Q(effective_to__isnull=True) | Q(effective_to__gte=payroll_run.period_start))
        .order_by("-effective_from", "-id")
        .first()
    )
    if ssf_contribution:
        ssf_employee_amount = (
            statutory_base_amount * to_decimal(ssf_contribution.employee_percent) / Decimal("100")
        ).quantize(Decimal("0.01"))
        ssf_employer_amount = (
            statutory_base_amount * to_decimal(ssf_contribution.employer_percent) / Decimal("100")
        ).quantize(Decimal("0.01"))
        statutory_rows.extend(
            [
                {
                    "salary_component": payroll_setting.ssf_employee_component if payroll_setting else None,
                    "source_type": "statutory",
                    "sequence": 972,
                    "amount": ssf_employee_amount,
                    "component_type": "deduction",
                    "tax_treatment": "non_taxable",
                    "calculation_trace": {
                        "statutory_type": "ssf_employee",
                        "percent": str(ssf_contribution.employee_percent),
                        "base_amount": str(statutory_base_amount),
                        "attendance_factor": str(attendance_factor),
                    },
                },
                {
                    "salary_component": payroll_setting.ssf_employer_component if payroll_setting else None,
                    "source_type": "statutory",
                    "sequence": 973,
                    "amount": ssf_employer_amount,
                    "component_type": "employer_contribution",
                    "tax_treatment": "non_taxable",
                    "calculation_trace": {
                        "statutory_type": "ssf_employer",
                        "percent": str(ssf_contribution.employer_percent),
                        "base_amount": str(statutory_base_amount),
                        "attendance_factor": str(attendance_factor),
                    },
                },
            ]
        )

    component_rows.extend([row for row in statutory_rows if row["amount"] > 0])
    return component_rows


def _apply_income_tax(*, payroll_run: PayrollRun, assignment: EmployeeSalaryAssignment, component_rows, totals):
    fiscal_year = _get_fiscal_year_for_run(payroll_run)
    if not fiscal_year:
        return totals, component_rows
    payroll_setting = _get_payroll_setting(payroll_run)

    slabs = list(TaxSlab.objects.filter(fiscal_year=fiscal_year, is_active=True).order_by("min_income", "id"))
    if not slabs:
        return totals, component_rows

    declaration = EmployeeTaxDeclaration.objects.filter(
        employee=assignment.employee,
        fiscal_year=fiscal_year,
    ).first()
    declaration_deduction = Decimal("0.00")
    if declaration:
        declaration_deduction = (
            to_decimal(declaration.declared_amount)
            + to_decimal(declaration.investment_amount)
            + to_decimal(declaration.insurance_amount)
            + to_decimal(declaration.other_deductions)
        )

    factor = _payment_period_factor(assignment.payment_frequency)
    annual_taxable_income = max(
        (to_decimal(totals["taxable_income"]) * factor) - declaration_deduction,
        Decimal("0.00"),
    )
    annual_tax = _calculate_tax_from_slabs(annual_taxable_income, slabs)
    period_tax = (annual_tax / factor).quantize(Decimal("0.01")) if factor else Decimal("0.00")

    if period_tax > 0:
        component_rows.append(
            {
                "salary_component": payroll_setting.tax_deduction_component if payroll_setting else None,
                "source_type": "tax",
                "sequence": 980,
                "amount": period_tax,
                "component_type": "deduction",
                "tax_treatment": "non_taxable",
                "calculation_trace": {
                    "fiscal_year": str(fiscal_year),
                    "annual_taxable_income": str(annual_taxable_income),
                    "annual_tax": str(annual_tax),
                    "period_factor": str(factor),
                    "declaration_deduction": str(declaration_deduction),
                },
            }
        )
        totals["income_tax"] = period_tax
        totals["total_deductions"] = (to_decimal(totals["total_deductions"]) + period_tax).quantize(Decimal("0.01"))
        totals["net_salary"] = (to_decimal(totals["gross_earnings"]) - to_decimal(totals["total_deductions"])).quantize(
            Decimal("0.01")
        )

    return totals, component_rows


def _build_payslip_number(*, payroll_run: PayrollRun, payroll_employee: PayrollRunEmployee):
    employee_code = payroll_employee.employee.employee_id or payroll_employee.employee_id
    return f"PS-RUN{payroll_run.id}-{payroll_run.payroll_year}-{payroll_run.payroll_month:02d}-{employee_code}"


def _create_or_update_payslip(*, payroll_run: PayrollRun, payroll_employee: PayrollRunEmployee):
    Payslip.objects.update_or_create(
        payroll_run_employee=payroll_employee,
        defaults={
            "payslip_number": _build_payslip_number(payroll_run=payroll_run, payroll_employee=payroll_employee),
            "generated_date": timezone.localdate(),
            "email_sent": False,
        },
    )


def _log_payroll_action(*, payroll_run: PayrollRun, action: str, acting_user=None, old_data=None, new_data=None):
    PayrollLog.objects.create(
        payroll_run=payroll_run,
        action=action,
        performed_by=acting_user,
        old_data=old_data,
        new_data=new_data,
    )


def _has_active_payroll_lock(payroll_run: PayrollRun) -> bool:
    lock_exists = PayrollLock.objects.filter(payroll_run=payroll_run).exists()
    if not lock_exists:
        return False
    if payroll_run.status in {"approved", "locked"}:
        return True
    PayrollLock.objects.filter(payroll_run=payroll_run).delete()
    return False


def _merge_component_rows_for_save(component_rows):
    merged_rows = []
    indexed_rows = {}

    for row in component_rows:
        salary_component = row.get("salary_component")
        if salary_component is None:
            continue

        key = salary_component.pk
        existing = indexed_rows.get(key)
        if existing is None:
            normalized = dict(row)
            trace = normalized.get("calculation_trace") or {}
            normalized["calculation_trace"] = trace if isinstance(trace, dict) else {"value": trace}
            indexed_rows[key] = normalized
            merged_rows.append(normalized)
            continue

        existing["amount"] = to_decimal(existing.get("amount")) + to_decimal(row.get("amount"))
        existing_quantity = existing.get("quantity")
        row_quantity = row.get("quantity")
        if existing_quantity is not None or row_quantity is not None:
            existing["quantity"] = to_decimal(existing_quantity) + to_decimal(row_quantity)
        existing_rate = existing.get("rate")
        if existing_rate in (None, "") and row.get("rate") not in (None, ""):
            existing["rate"] = row.get("rate")
        existing["sequence"] = min(existing.get("sequence", 1), row.get("sequence", 1))

        existing_trace = existing.get("calculation_trace") or {}
        if not isinstance(existing_trace, dict):
            existing_trace = {"value": existing_trace}
        existing_sources = existing_trace.setdefault("merged_sources", [])
        existing_sources.append(
            {
                "source_type": row.get("source_type"),
                "amount": str(row.get("amount")),
                "quantity": str(row.get("quantity") or ""),
                "rate": str(row.get("rate") or ""),
                "trace": row.get("calculation_trace") or {},
            }
        )
        existing["calculation_trace"] = existing_trace

    return merged_rows


@transaction.atomic
def process_payroll_run(*, payroll_run: PayrollRun, acting_user):
    if payroll_run.status == "locked" or _has_active_payroll_lock(payroll_run):
        raise ValueError("Locked payroll runs cannot be processed.")
    if payroll_run.status not in {"draft", "processed"}:
        raise ValueError("Only draft or processed payroll runs can be recalculated.")

    build_attendance_payroll_inputs(payroll_run=payroll_run)
    build_leave_payroll_inputs(payroll_run=payroll_run)

    PayrollRunComponent.objects.filter(payroll_run_employee__payroll_run=payroll_run).delete()
    Payslip.objects.filter(payroll_run_employee__payroll_run=payroll_run).delete()
    PayrollRunEmployee.objects.filter(payroll_run=payroll_run).delete()

    assignments = []
    seen_employee_ids = set()
    for assignment in get_active_salary_assignments(payroll_run=payroll_run):
        if assignment.employee_id in seen_employee_ids:
            continue
        seen_employee_ids.add(assignment.employee_id)
        assignments.append(assignment)

    total_gross = Decimal("0.00")
    total_deductions = Decimal("0.00")
    total_net = Decimal("0.00")
    employee_count = 0

    for assignment in assignments:
        try:
            component_rows = _build_component_rows(assignment)
            component_rows, attendance_context = _apply_attendance_proration(
                payroll_run=payroll_run,
                assignment=assignment,
                component_rows=component_rows,
            )
            component_rows = _append_leave_and_adjustment_rows(
                payroll_run=payroll_run,
                assignment=assignment,
                component_rows=component_rows,
            )
            component_rows = _append_overtime_rows(
                payroll_run=payroll_run,
                assignment=assignment,
                component_rows=component_rows,
            )
            component_rows = _build_statutory_rows(
                payroll_run=payroll_run,
                assignment=assignment,
                component_rows=component_rows,
            )
            totals = _calculate_totals(component_rows)
            totals, component_rows = _apply_income_tax(
                payroll_run=payroll_run,
                assignment=assignment,
                component_rows=component_rows,
                totals=totals,
            )
            payroll_employee = PayrollRunEmployee.objects.create(
                payroll_run=payroll_run,
                employee=assignment.employee,
                employee_salary_assignment=assignment,
                salary_structure_name=assignment.salary_structure.name,
                gross_salary=assignment.gross_salary,
                gross_earnings=totals["gross_earnings"],
                total_deductions=totals["total_deductions"],
                employer_contributions=totals["employer_contributions"],
                taxable_income=totals["taxable_income"],
                income_tax=totals["income_tax"],
                net_salary=totals["net_salary"],
                status="processed",
                calculation_summary={
                    "component_count": len(component_rows),
                    "salary_structure_code": assignment.salary_structure.code,
                    "attendance": attendance_context or {},
                },
            )

            payroll_component_rows = _merge_component_rows_for_save(component_rows)
            PayrollRunComponent.objects.bulk_create(
                [
                    PayrollRunComponent(
                        payroll_run_employee=payroll_employee,
                        salary_component=row["salary_component"],
                        source_type=row["source_type"],
                        sequence=row["sequence"],
                        quantity=row.get("quantity"),
                        rate=row.get("rate"),
                        amount=row["amount"],
                        calculation_trace=row["calculation_trace"],
                    )
                    for row in payroll_component_rows
                ]
            )
            _create_or_update_payslip(payroll_run=payroll_run, payroll_employee=payroll_employee)

            total_gross += totals["gross_earnings"]
            total_deductions += totals["total_deductions"]
            total_net += totals["net_salary"]
            employee_count += 1
        except FormulaEvaluationError as exc:
            PayrollRunEmployee.objects.create(
                payroll_run=payroll_run,
                employee=assignment.employee,
                employee_salary_assignment=assignment,
                salary_structure_name=assignment.salary_structure.name,
                gross_salary=assignment.gross_salary,
                status="error",
                remarks=str(exc),
                calculation_summary={"error": str(exc)},
            )
            employee_count += 1

    payroll_run.status = "processed"
    payroll_run.processed_at = timezone.now()
    payroll_run.processed_by = acting_user
    payroll_run.employee_count = employee_count
    payroll_run.total_gross = total_gross.quantize(Decimal("0.01"))
    payroll_run.total_deductions = total_deductions.quantize(Decimal("0.01"))
    payroll_run.total_net = total_net.quantize(Decimal("0.01"))
    payroll_run.save(
        update_fields=[
            "status",
            "processed_at",
            "processed_by",
            "employee_count",
            "total_gross",
            "total_deductions",
            "total_net",
            "updated_at",
        ]
    )
    _log_payroll_action(
        payroll_run=payroll_run,
        action="processed",
        acting_user=acting_user,
        new_data={
            "employee_count": employee_count,
            "total_gross": str(payroll_run.total_gross),
            "total_deductions": str(payroll_run.total_deductions),
            "total_net": str(payroll_run.total_net),
        },
    )
    return payroll_run


@transaction.atomic
def reset_payroll_run(*, payroll_run: PayrollRun):
    if payroll_run.status == "locked" or _has_active_payroll_lock(payroll_run):
        raise ValueError("Locked payroll runs cannot be reset.")
    if payroll_run.status not in {"processed", "reviewed", "approved"}:
        raise ValueError("Only processed payroll runs can be reset to draft.")
    old_data = {
        "status": payroll_run.status,
        "employee_count": payroll_run.employee_count,
        "total_gross": str(payroll_run.total_gross),
        "total_deductions": str(payroll_run.total_deductions),
        "total_net": str(payroll_run.total_net),
    }
    PayrollRunComponent.objects.filter(payroll_run_employee__payroll_run=payroll_run).delete()
    Payslip.objects.filter(payroll_run_employee__payroll_run=payroll_run).delete()
    PayrollRunEmployee.objects.filter(payroll_run=payroll_run).delete()
    PayrollApproval.objects.filter(payroll_run=payroll_run).delete()
    payroll_run.status = "draft"
    payroll_run.processed_at = None
    payroll_run.processed_by = None
    payroll_run.approved_at = None
    payroll_run.approved_by = None
    payroll_run.employee_count = 0
    payroll_run.total_gross = Decimal("0.00")
    payroll_run.total_deductions = Decimal("0.00")
    payroll_run.total_net = Decimal("0.00")
    payroll_run.save(
        update_fields=[
            "status",
            "processed_at",
            "processed_by",
            "approved_at",
            "approved_by",
            "employee_count",
            "total_gross",
            "total_deductions",
            "total_net",
            "updated_at",
        ]
    )
    _log_payroll_action(
        payroll_run=payroll_run,
        action="reset",
        old_data=old_data,
        new_data={"status": "draft"},
    )
    return payroll_run


@transaction.atomic
def approve_payroll_run(*, payroll_run: PayrollRun, acting_user):
    if payroll_run.status not in {"processed", "reviewed"}:
        raise ValueError("Only processed or reviewed payroll runs can be approved.")
    if payroll_run.status == "locked" or _has_active_payroll_lock(payroll_run):
        raise ValueError("Locked payroll runs cannot be approved.")

    last_approval = payroll_run.approvals.order_by("-approval_level", "-id").first()
    level = (last_approval.approval_level + 1) if last_approval else 1
    PayrollApproval.objects.create(
        payroll_run=payroll_run,
        approval_level=level,
        approved_by=acting_user,
        status="approved",
        approved_at=timezone.now(),
        remarks="Approved from payroll run action.",
    )
    payroll_run.status = "approved"
    payroll_run.approved_at = timezone.now()
    payroll_run.approved_by = acting_user
    payroll_run.save(update_fields=["status", "approved_at", "approved_by", "updated_at"])
    _log_payroll_action(
        payroll_run=payroll_run,
        action="approved",
        acting_user=acting_user,
        new_data={"approval_level": level, "status": "approved"},
    )
    return payroll_run


@transaction.atomic
def lock_payroll_run(*, payroll_run: PayrollRun, acting_user):
    if payroll_run.status != "approved":
        raise ValueError("Only approved payroll runs can be locked.")

    lock_record, created = PayrollLock.objects.get_or_create(
        payroll_run=payroll_run,
        defaults={
            "locked_by": acting_user,
            "locked_at": timezone.now(),
            "remarks": "Locked from payroll run action.",
        },
    )
    if not created:
        raise ValueError("This payroll run is already locked.")

    payroll_run.status = "locked"
    payroll_run.locked_at = lock_record.locked_at
    payroll_run.save(update_fields=["status", "locked_at", "updated_at"])
    _log_payroll_action(
        payroll_run=payroll_run,
        action="locked",
        acting_user=acting_user,
        new_data={"locked_at": lock_record.locked_at.isoformat()},
    )
    return payroll_run
