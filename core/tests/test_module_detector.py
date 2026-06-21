from django.test import SimpleTestCase

from core.services.module_detector import ModuleDetectorService


class ModuleDetectorServiceTests(SimpleTestCase):
    def setUp(self):
        self.service = ModuleDetectorService()

    def test_detect_returns_rich_metadata_for_known_area(self):
        info = self.service.detect("/crm/leads/")

        self.assertEqual(info.module_name, "crm")
        self.assertEqual(info.display_name, "CRM")
        self.assertEqual(info.icon, "briefcase")
        self.assertIn("sales", info.domains)
        self.assertTrue(info.is_known)
        self.assertEqual(info.layout_template, "crm/layouts/base.html")
        self.assertEqual(info.metadata["kind"], "module")

    def test_detect_falls_back_to_default_metadata_for_unknown_area(self):
        info = self.service.detect("/not-a-module/dashboard/")

        self.assertEqual(info.module_name, "not-a-module")
        self.assertEqual(info.display_name, "Not A Module")
        self.assertEqual(info.icon, "circle")
        self.assertEqual(info.domains, ())
        self.assertFalse(info.is_known)
        self.assertEqual(info.layout_template, "layouts/base.html")

