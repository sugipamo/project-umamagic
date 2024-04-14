from django.urls import path
from .views import events
from .views import login_required

app_name = 'scraping'
urlpatterns = [
    path('event_schedule_list/', events.EventScheduleListView.as_view(), name='event_schedule_list'),
    path('login_required_form/', login_required.login_required_form, name='login_required_form'),
]