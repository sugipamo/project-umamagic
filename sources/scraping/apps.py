from django.apps import AppConfig


class ScrapingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'scraping'

    def ready(self):
        from .models import events
        events.doevents_scheduler()