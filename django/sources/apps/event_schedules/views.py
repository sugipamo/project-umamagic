from django.shortcuts import render
from django.utils import timezone

from django.http import HttpResponse
from django.shortcuts import redirect

from django.views.generic import ListView
from .models import Schedule, ScheduleDoeventHistory
from .models import doevent

class EventScheduleListView(ListView):
    model = Schedule
    template_name = 'event_schedules/event_schedule_list.html'
    def queryset(self):
        return Schedule.objects.all().order_by('event_function')

class ScheduleDoEventHistoryListView(ListView):
    model = ScheduleDoeventHistory
    template_name = 'event_schedules/event_schedule_doevent_history.html'

    def get_queryset(self):
        pk = self.kwargs.get('pk')  # URLからpkを取得
        return ScheduleDoeventHistory.objects.filter(schedule=pk).order_by('created_at').reverse()
    
def redirect_event_schedule_list(request):
    return redirect('event_schedules:event_schedule_list')

def event_schedule_solve_error(request, pk):
    event_schedule = Schedule.objects.get(pk=pk)
    event_schedule.status = 1
    event_schedule.save()
    return redirect('event_schedules:event_schedule_list')

def event_schedule_manual_doevent(request, pk):
    event_schedule = Schedule.objects.get(pk=pk)
    event_schedule.nextexecutedatetime = timezone.now()
    return_value = event_schedule.doevent()
    return HttpResponse("<html><body>"+ str(return_value).replace("\n", "<br>") + "</body></html>")
    return redirect('event_schedules:event_schedule_list')


def event_schedule_doevent(request):
    return HttpResponse("<html><body>"+ str(doevent()).replace("\n", "<br>") + "</body></html>")