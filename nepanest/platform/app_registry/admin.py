from django.contrib import admin

from .models import Client, License, LicenseRenewHistory, Subscription, TenantDB


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = (
        "business_name",
        "client_code",
        "contact_email",
        "contact_phone",
        "plan",
        "status",
        "registered_on",
    )
    list_filter = ("plan", "status", "registered_on")
    search_fields = ("business_name", "client_code", "contact_email", "contact_phone")
    ordering = ("-registered_on",)


@admin.register(TenantDB)
class TenantDBAdmin(admin.ModelAdmin):
    list_display = (
        "client",
        "db_name",
        "db_user",
        "db_host",
        "db_port",
        "status",
    )
    list_filter = ("status", "db_host")
    search_fields = ("client__business_name", "client__client_code", "db_name", "db_user", "db_host")
    ordering = ("db_name",)


@admin.register(License)
class LicenseAdmin(admin.ModelAdmin):
    list_display = (
        "client",
        "plan",
        "issued_on",
        "expires_on",
        "max_users",
        "max_branches",
        "grace_days",
        "is_current",
    )
    list_filter = ("plan", "is_current", "issued_on", "expires_on")
    search_fields = ("client__business_name", "client__client_code", "plan")
    ordering = ("-issued_on",)


@admin.register(LicenseRenewHistory)
class LicenseRenewHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "license",
        "old_expiry",
        "new_expiry",
        "renewed_by",
        "renewed_at",
    )
    list_filter = ("renewed_at",)
    search_fields = ("license__client__business_name", "license__client__client_code", "renewed_by", "notes")
    ordering = ("-renewed_at",)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "client",
        "plan_name",
        "amount",
        "interval",
        "status",
        "period_start",
        "period_end",
    )
    list_filter = ("status", "interval", "period_start", "period_end")
    search_fields = ("client__business_name", "client__client_code", "plan_name", "interval", "status")
    ordering = ("-period_end",)
