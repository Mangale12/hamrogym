from django.db import models

# Create your models here.
from .asset import Asset, AssetDocument
from .asset_assignment import AssetAssignment
from .asset_category import AssetCategory
from .asset_condition import AssetCondition
from .depreciation import AssetDepreciationRegister
from .asset_location import AssetLocation
from .asset_maintenance import AssetMaintenanceRecord
from .asset_transfer import AssetTransfer
from .asset_status import AssetStatus
from .asset_vendor import AssetVendor
from .asset_type import AssetType
from .asset_incident_type import AssetIncidentType
from .asset_incident import AssetIncident
