from django.apps import AppConfig
# from django.apps import apps

class DynamicTablesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dynamic_tables'

    def ready(self):
        pass