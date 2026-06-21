from django.db import models


class Subscription(models.Model):
    """
    Tracks the active subscription details for a client.
    """

    client = models.ForeignKey(
        "app_registry.Client",
        on_delete=models.CASCADE,
        related_name="subscriptions",
    )
    plan_name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    interval = models.CharField(max_length=50)
    status = models.CharField(max_length=20)
    period_start = models.DateField()
    period_end = models.DateField()

    class Meta:
        ordering = ["-period_end", "-id"]
        verbose_name = "Subscription"
        verbose_name_plural = "Subscriptions"
        db_table = "app_registry_subscriptions"

    def __str__(self):
        return f"{self.client} - {self.plan_name} ({self.period_start} to {self.period_end})"



class Invoice(models.Model):
    """
    Represents an invoice generated for a subscription.
    """

    subscription = models.ForeignKey(
        "app_registry.Subscription",
        on_delete=models.CASCADE,
        related_name="invoices",
    )
    invoice_number = models.CharField(max_length=50, unique=True)
    amount_due = models.DecimalField(max_digits=12, decimal_places=2)
    due_date = models.DateField()
    payment_date = models.DateField(null=True, blank=True)
    currency = models.ForeignKey("core.Currency", verbose_name="Currency", on_delete=models.CASCADE)
    status = models.CharField(max_length=20)

    class Meta:
        ordering = ["-due_date", "-id"]
        verbose_name = "Invoice"
        verbose_name_plural = "Invoices"
        db_table = "app_registry_invoices"

    def __str__(self):
        return f"Invoice {self.invoice_number} for {self.subscription.client}"