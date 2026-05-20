from django.db import models
from core.mixins.erp import ERPBaseModel
from django.utils.translation import gettext_lazy as _

class LeadSource(ERPBaseModel):
    name = models.CharField(_("Name"), max_length=255, unique=True)
    is_default = models.BooleanField(_("Is Default"), default=False)
    code = models.CharField(_("Code"), max_length=50, unique=True)

    def __str__(self):
        return self.name