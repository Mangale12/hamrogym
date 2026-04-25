from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = "core"

    def ready(self):
        import nepanest.common.helpers.register
        from core.registry import autodiscover_entities

        autodiscover_entities()
