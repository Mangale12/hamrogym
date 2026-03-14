from django.db import models

class OrganizationSettings(models.Model):
    CALENDAR_CHOICES = [
        ("AD", "AD"),
        ("BS", "BS"),
    ]
    name = models.CharField(max_length=25, unique=True, null=True, blank=True, help_text="Name of the organization")
    registration_number = models.CharField(max_length=100, unique=True, null=True, blank=True, help_text="Registration number of the organization")
    pan_vat_number = models.CharField(max_length=100, unique=True, null=True, blank=True, help_text="PAN/VAT number of the organization")
    phone = models.CharField(max_length=20, null=True, blank=True, help_text="Phone number of the organization")
    email = models.EmailField(null=True, blank=True, help_text="Email address of the organization")
    website = models.URLField(null=True, blank=True, help_text="Website URL of the organization")
    logo = models.ImageField(upload_to='organization_logos/', null=True, blank=True, help_text="Logo of the organization")
    address = models.TextField(null=True, blank=True, help_text="Address of the organization")
    contact_person = models.CharField(max_length=100, null=True, blank=True, help_text="Name of the contact person")
    calendar = models.CharField(max_length=2, choices=CALENDAR_CHOICES, null=True, blank=True, help_text="Calendar type")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
