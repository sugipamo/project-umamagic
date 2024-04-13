from django.contrib import admin

# Register your models here.


from .models.events import EventCategory, EventSchedule

admin.site.register(EventCategory)
admin.site.register(EventSchedule)
