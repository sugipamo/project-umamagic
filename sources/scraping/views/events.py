from django.shortcuts import render

from django.views.generic import ListView
from ..models.events import EventSchedule

class EventScheduleListView(ListView):
    model = EventSchedule
    template_name = 'scraping/event_schedule_list.html'

    def queryset(self):
        return EventSchedule.objects.all().order_by('latestcalled_at')
    