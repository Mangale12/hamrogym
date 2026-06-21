from django.db import models


class Tenant(models.Model):

    STATUS_CHOICES = [
        ("active",    "Active"),
        ("suspended", "Suspended"),
        ("expired",   "Expired"),
        ("trial",     "Trial"),
    ]

    name        = models.CharField(max_length=200)
    code        = models.CharField(max_length=50, unique=True)
    db_name     = models.CharField(max_length=100, unique=True)
    db_user     = models.CharField(max_length=100)
    db_password = models.CharField(max_length=200)
    db_host     = models.CharField(max_length=200, default="127.0.0.1")
    db_port     = models.CharField(max_length=10,  default="3306")
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default="trial")
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "platform_tenants"

    @property
    def database_alias(self) -> str:
        return f"db_erp_{self.code}"

    def __str__(self):
        return f"{self.name} ({self.code})"