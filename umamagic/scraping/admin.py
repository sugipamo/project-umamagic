from django.contrib import admin

# Register your models here.


from .models import ScrapeCategory, EventSchedule

admin.site.register(ScrapeCategory)
admin.site.register(EventSchedule)
