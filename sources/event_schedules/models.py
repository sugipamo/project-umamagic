from django.utils import timezone
from django.db import models
import traceback

ACCEPT_IMPORTS = ["django", "event_schedules"]

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
        variables = []
        for property_ in dir(self.schedule):
            try:
                variables.append("{}: {}".format(property_, getattr(self.schedule, property_)))
            except:
                pass
        self.variables = "\n".join(variables)
        super().save()

    def __str__(self):
        return self.schedule.title

class Schedule(models.Model):
    title = models.CharField(max_length=255)
    status = models.IntegerField(choices=[(i+1, s) for i, s in enumerate(["待機", "実行中", "完了", "エラー"])], default=1)
    event_function = models.CharField(max_length=255)
    nextexecutedatetime = models.DateTimeField(default=timezone.now)
    schedule_str_default = models.CharField(max_length=255, null=True, blank=True, default="0")
    schedule_str = models.CharField(max_length=255, null=True, blank=True, default=",")
    latestcalled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def __parse_schedule_str(self, schedule_str):
        def schedule_str_to_que(schedule_str): return str(schedule_str).split(",")[::-1]
        if schedule_str is None:
            schedule_str = self.schedule_str_default
        needdo, nextexecutedatetime, schedule_str = False, None, schedule_str_to_que(schedule_str)

        while schedule_str and nextexecutedatetime is None:
            s = schedule_str.pop()
            if s.replace(" ", "") == "":
                if self.schedule_str_default == "":
                    schedule_str = None
                else:   
                    schedule_str = schedule_str_to_que(self.schedule_str_default)
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
        
        needdo, nextexecutedatetime, schedule_str = self.__parse_schedule_str(self.schedule_str)
        if needdo:
            event_history = ScheduleDoeventHistory(schedule=self)
            try:
                self.status = 2
                self.save()
                import_str = self.event_function.split(".")[0]
                # いったんこれですすめるが、セキュリティの問題があるため
                # 本番環境移行時には適切な対策を行うこと。
                if import_str not in ACCEPT_IMPORTS:
                    raise ScheduleExecutuionError(f"{import_str}はimportできません。")
                exec("import {}".format())
                exec(f"{self.event_function}")

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
        event_history.save()
        return str(event_history.variables)


def doevent():
    now = timezone.now()
    event = Schedule.objects.filter(status=1, nextexecutedatetime__lte=now).order_by("latestcalled_at")
    if event.exists():
        try:
            return event.first().doevent()
        except Exception as e:
            with open("error.log", "a") as f:
                f.write(f"{timezone.now()}: {str(e)}\n{traceback.format_exc()}\n\n")
            raise e
    return "Event has not been found."