from django.urls import path
from .views import events
from .views import login_required

app_name = 'scraping'
urlpatterns = [
    path('event_schedule_list/', events.EventScheduleListView.as_view(), name='event_schedule_list'),
    path('login_required_form/', login_required.login_required_detail, name='login_required_form'),
    path('login_required_list/', login_required.LoginRequiredListView.as_view(), name='login_required_list'),
    path('login_required_detail/<int:pk>/', login_required.login_required_detail, name='login_required_detail'),
]