from django.shortcuts import render

from django.views.generic import ListView
from .models import CrawlSchedule

class CrawlScheduleListView(ListView):
    model = CrawlSchedule
    template_name = 'scraping/crawl_schedule_list.html'

    def query_set(self):
        return CrawlSchedule.objects.filter(deleted_at__isnull=True)