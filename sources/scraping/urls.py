from django.urls import path
from .views import events
from .views import login_for_scraping

app_name = 'scraping'
urlpatterns = [
    path('', events.EventScheduleListView.as_view(), name='event_schedule_list'),
    path('event_schedule_list/', events.EventScheduleListView.as_view(), name='event_schedule_list'),
    path('login_for_scraping_form/', login_for_scraping.login_for_scraping_detail, name='login_for_scraping_form'),
    path('login_for_scraping_list/', login_for_scraping.LoginForScrapingListView.as_view(), name='login_for_scraping_list'),
    path('login_for_scraping_detail/<int:pk>/', login_for_scraping.login_for_scraping_detail, name='login_for_scraping_detail'),
]