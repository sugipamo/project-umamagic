from django.shortcuts import render
from django.shortcuts import redirect

from django.views.generic import ListView
from ..models.events import EventSchedule
from scraping.models.events import doevent

class EventScheduleListView(ListView):
    model = EventSchedule
    template_name = 'scraping/event_schedule_list.html'

    def queryset(self):
        return EventSchedule.objects.all().order_by('latestcalled_at') 

def event_chedule_doevent(request):
    doevent()
    return redirect('scraping:event_schedule_list')

def redirect_event_schedule_list(request):
    return redirect('scraping:event_schedule_list')

def event_schedule_solve_error(request, pk):
    event_schedule = EventSchedule.objects.get(pk=pk)
    event_schedule.status = 1
    event_schedule.errormessage = ""
    event_schedule.save()
    return redirect('scraping:event_schedule_list')