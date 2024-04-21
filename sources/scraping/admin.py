from django.contrib import admin

# Register your models here.


from .models.events import EventCategory, EventSchedule
from .models.login_for_scraping import LoginForScraping


from django.contrib import admin
from .models import EventSchedule, EventArgs

class EventArgsInline(admin.TabularInline):
    model = EventArgs
    extra = 1  # Number of extra forms to display

class EventScheduleAdmin(admin.ModelAdmin):
    inlines = [EventArgsInline]


admin.site.register(EventCategory)
admin.site.register(EventSchedule, EventScheduleAdmin)
admin.site.register(LoginForScraping)


