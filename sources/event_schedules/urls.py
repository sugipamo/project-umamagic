from django.urls import path
from . import views

app_name = 'event_schedules'
urlpatterns = [
    path('doevent/', views.event_schedule_doevent, name='doevent'),
    path('', views.redirect_event_schedule_list, name='event_schedule_list'),
    path('event_schedule_list/', views.EventScheduleListView.as_view(), name='event_schedule_list'),
    path('event_schedule_doevent_history/<int:pk>/', views.ScheduleDoEventHistoryListView.as_view(), name='event_schedule_doevent_history'),
    path('event_schedule_solve_error/<int:pk>/', views.event_schedule_solve_error, name='event_schedule_solve_error'),
]