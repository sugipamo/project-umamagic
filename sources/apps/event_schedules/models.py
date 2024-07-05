from django.utils import timezone
from django.db import models
import traceback
from pathlib import Path
import importlib

event_functions = {}

class ScheduleExecutuionError(Exception):
    pass

class ScheduleDoeventHistory(models.Model):
    schedule = models.ForeignKey("Schedule", on_delete=models.CASCADE)
    variables = models.TextField(null=True, blank=True)
    event_function = models.CharField(max_length=255)
    error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self):
        self.event_function = self.schedule.event_function
        variables = [
            "---------------",
            "doevent datetime: " + str(timezone.now()),
            "schedule: " + str(self.schedule.event_function),
            "nextexecutedatetime: " + str(self.schedule.nextexecutedatetime),
            "error_message: " + str(self.error_message),
            "---------------",
        ]

        self.variables = "\n".join(variables)
        super().save()

    def __str__(self):
        return self.schedule.title

class Schedule(models.Model):
    status = models.IntegerField(choices=[(i+1, s) for i, s in enumerate(["待機", "実行中", "完了", "エラー"])], default=1)
    event_function = models.CharField(max_length=255)
    nextexecutedatetime = models.DateTimeField(default=timezone.now)
    schedule_str = models.CharField(max_length=255, null=True, blank=True, default=",")
    latestcalled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.event_function

    def __parse_schedule_str(self, schedule_str, schedule_str_default):
        def schedule_str_to_que(schedule_str): return str(schedule_str).split(",")[::-1]
        if schedule_str is None:
            schedule_str = schedule_str_default
        needdo, nextexecutedatetime, schedule_str = False, None, schedule_str_to_que(schedule_str)

        while schedule_str and nextexecutedatetime is None:
            s = schedule_str.pop()
            if s.replace(" ", "") == "":
                if schedule_str_default == "":
                    schedule_str = None
                else:   
                    schedule_str = schedule_str_to_que(schedule_str_default)
                continue

            if s.replace(" ", "") == "0":
                if needdo:
                    nextexecutedatetime = timezone.now()
                needdo = True
                continue

            nextexecutedatetime = timezone.now() + timezone.timedelta(seconds=int(s))

        if not nextexecutedatetime is None:
            schedule_str.append("0")
        
        if schedule_str:
            schedule_str = ",".join(str(r) for r in schedule_str[::-1])
        else:
            schedule_str = None
        return needdo, nextexecutedatetime, schedule_str

    def doevent(self):
        self.latestcalled_at = timezone.now()

        if self.status == 2:
            self.save()
            raise ScheduleExecutuionError(f"{self.title}は実行中です。")
        if self.status == 3:
            self.save()
            raise ScheduleExecutuionError(f"{self.title}は既に完了しています。")
        if self.status == 4:
            self.save()
            raise ScheduleExecutuionError(f"{self.title}はエラーが発生しています。")
        if not self.nextexecutedatetime is None and self.nextexecutedatetime > timezone.now():
            self.save()
            raise ScheduleExecutuionError(f"{self.title}はまだ実行できません。")
        
        event_function = event_functions.get(self.event_function)
        schedule_str_default = event_function.SCHEDULE_STR

        needdo, nextexecutedatetime, schedule_str = self.__parse_schedule_str(self.schedule_str, schedule_str_default)
        event_history = ScheduleDoeventHistory(schedule=self)
        if needdo:
            try:
                self.status = 2
                self.save()
                event_function.main()

            except Exception as e:
                event_history.error_message = f"{str(e)}\n{traceback.format_exc()}"
                event_history.save()
                self.status = 4
                self.save()
                raise e
            
        self.status = 1
        self.schedule_str = schedule_str
        self.nextexecutedatetime = nextexecutedatetime
        
        if nextexecutedatetime is None:
            self.nextexecutedatetime = timezone.now()
            self.status = 3
        self.save()
        if needdo:
            event_history.save()
        return str(event_history.variables)


def doevent():
    if len(event_functions) == 0:
        for event_function in Path("apps/event_schedules/events").glob("*.py"):
            event_function = event_function.stem
            if event_function == "__init__":
                continue
            event_functions[event_function] = importlib.import_module("apps.event_schedules.events." + event_function)

        for event_function in event_functions:
            Schedule.objects.get_or_create(event_function=event_function)

        schedules_to_delete = set(Schedule.objects.values_list('event_function', flat=True)) - set(event_functions.keys())
        Schedule.objects.filter(event_function__in=schedules_to_delete).delete()
        

    event = Schedule.objects.filter(status=1, nextexecutedatetime__lte=timezone.now()).order_by("latestcalled_at")
    if event.exists():
        try:
            return event.first().doevent()
        except Exception as e:
            with open("error.log", "a") as f:
                f.write(f"{timezone.now()}: {str(e)}\n{traceback.format_exc()}\n\n")
            raise e
    return "Event has not been found."