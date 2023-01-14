from django.apps import AppConfig


class GreatestinvestappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'greatestinvestapp'

    def ready(self):
    	import greatestinvestapp.signals
