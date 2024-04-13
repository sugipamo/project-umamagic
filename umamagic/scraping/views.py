from django.shortcuts import render

from django.views.generic import ListView
from .models.events import EventSchedule

class EventScheduleListView(ListView):
    model = EventSchedule
    template_name = 'scraping/event_schedule_list.html'

    def query_set(self):
        return EventSchedule.objects.filter(deleted_at__isnull=True)