from django.contrib import admin

# Register your models here.


from .models.events import EventCategory, EventSchedule
from .models.login_required import LoginRequired

admin.site.register(EventCategory)
admin.site.register(EventSchedule)
admin.site.register(LoginRequired)


