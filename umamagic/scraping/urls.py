from django.urls import path
from . import views

app_name = 'scraping'
urlpatterns = [
    path('event_schedule/', views.EventScheduleListView.as_view(), name='event_schedule_list'),
]