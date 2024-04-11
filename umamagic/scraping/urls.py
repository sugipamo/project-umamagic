from django.urls import path
from . import views

app_name = 'scraping'
urlpatterns = [
    path('crawl_schedule/', views.CrawlScheduleListView.as_view(), name='crawl_schedule_list'),
]