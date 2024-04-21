from django.contrib import admin

# Register your models here.


from .models.events import EventCategory, EventSchedule
from .models.login_for_scraping import LoginForScraping

admin.site.register(EventCategory)
admin.site.register(EventSchedule)
admin.site.register(LoginForScraping)


