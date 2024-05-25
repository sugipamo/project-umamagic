from django.urls import path
from .views import events
from .views import login_for_scraping

app_name = 'scraping'
urlpatterns = [
    path('', events.redirect_event_schedule_list, name='event_schedule_list'),
    path('doevent/', events.event_schedule_doevent, name='doevent'),
    path('event_schedule_list/', events.EventScheduleListView.as_view(), name='event_schedule_list'),
    path('event_schedule_solve_error/<int:pk>/', events.event_schedule_solve_error, name='event_schedule_solve_error'),
    path('login_for_scraping_form/', login_for_scraping.login_for_scraping_detail, name='login_for_scraping_form'),
    path('login_for_scraping_list/', login_for_scraping.LoginForScrapingListView.as_view(), name='login_for_scraping_list'),
    path('login_for_scraping_detail/<int:pk>/', login_for_scraping.login_for_scraping_detail, name='login_for_scraping_detail'),
]