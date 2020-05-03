from django.apps import AppConfig


class MohtechConfig(AppConfig):
    name = 'MohTech'

    def ready(self):
        import MohTech.signals
