from django.db import models
from django.utils import timezone
from scraping.model_utilitys.webdriver import WebDriver
from scraping.model_utilitys import event_methods
from apscheduler.schedulers.background import BackgroundScheduler
from scraping.models.login_for_scraping import LoginForScraping
from django.conf import settings
from django.core.signals import request_started
from django.dispatch import receiver
import traceback
from django.core.exceptions import ValidationError

class ScheduleError(Exception):
    pass

class EventCategory(models.Model):
    name = models.CharField(max_length=255)
    use_method = models.CharField(max_length=255, default="test.default_methods")
    need_driver = models.BooleanField(default=False)
    page_load_strategy = models.CharField(max_length=255, default="eager")
    schedule_str = models.CharField(max_length=255, default="0")
    parallel_limit = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if not self.schedule_str or self.schedule_str.isspace():
            raise ValidationError("schedule_str cannot be empty or whitespace only.")

    def doevent(self, **kwargs):
        method = event_methods
        for s in self.use_method.split("."):
            method = getattr(method, s)
        if self.need_driver:                
            with WebDriver(self.page_load_strategy) as driver:
                kwargs["driver"] = driver
                method(**kwargs)
        else:
            method(**kwargs)
        return f"{self.name}のイベントを実行しました。"

    def __str__(self):
        return self.name

class EventSchedule(models.Model):
    title = models.CharField(max_length=255)
    category = models.ForeignKey(EventCategory, on_delete=models.PROTECT)
    status = models.IntegerField(choices=[(i+1, s) for i, s in enumerate(["待機", "実行中", "完了", "エラー"])], default=1)
    nextexecutedatetime = models.DateTimeField(default=timezone.now, null=True, blank=True)
    schedule_str = models.CharField(max_length=255, default="0")
    latestcalled_at = models.DateTimeField(null=True, blank=True)
    errormessage = models.TextField(null=True, blank=True)
    memo = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.category.pk:
            self.category.save()
        super().save(*args, **kwargs)

    def set_args(self, key, value):
        self.save()
        try:
            eventargs = self.eventargs_set.get(key=key)
            eventargs.value = value
            eventargs.save()
        except:
            self.eventargs_set.create(key=key, value=value).save()

    def get_args(self, key):
        try:
            return self.eventargs_set.get(key=key).value
        except:
            return None

    def parse_schedule_str(self, schedule_str):
        def schedule_str_to_que(schedule_str): return str(schedule_str).split(",")[::-1]
        needdo, nextexecutedatetime, schedule_str = False, None, schedule_str_to_que(schedule_str)

        while schedule_str and nextexecutedatetime is None:
            s = schedule_str.pop()
            if s.replace(" ", "") == "":
                if self.category.schedule_str == "":
                    schedule_str = None
                else:   
                    schedule_str = schedule_str_to_que(self.category.schedule_str)
                continue

            if s.replace(" ", "") == "0":
                if needdo:
                    nextexecutedatetime = timezone.now()
                needdo = True
                continue

            dodate = [timezone.now().year, timezone.now().month, timezone.now().day, timezone.now().hour, timezone.now().minute, timezone.now().second]
            for i, d in enumerate(s.split()[::-1]):
                dodate[-i-1] = int(d)

            dodate = timezone.datetime(*dodate)

            if dodate == timezone.now():
                needdo = True
                continue
            
            if dodate < timezone.now():
                dodate = dodate + timezone.timedelta(*([1] + [0]*len(s.split())))

            nextexecutedatetime = dodate

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
            raise ScheduleError(f"{self.title}は実行中です。")
        if self.status == 3:
            self.save()
            raise ScheduleError(f"{self.title}は既に完了しています。")
        if self.status == 4:
            self.save()
            raise ScheduleError(f"{self.title}はエラーが発生しています。")
        if self.nextexecutedatetime > timezone.now():
            self.save()
            raise ScheduleError(f"{self.title}はまだ実行できません。")
        
        self.status = 2
        self.save()
        
        needdo, self.nextexecutedatetime, self.schedule_str = self.parse_schedule_str(self.schedule_str)
        if needdo:
            try:
                ret = self.category.doevent(**{d["key"]: d["value"] for d in self.eventargs_set.all().values()} if self.pk else {})
            except Exception as e:
                self.status = 4
                self.errormessage = f"{str(e)}\n{traceback.format_exc()}"
                self.save()
                raise e
            
        if self.nextexecutedatetime is None:
            self.status = 3

        self.save()
        return True

    def __str__(self):
        return self.title
    
class EventArgs(models.Model):
    event_schedule = models.ForeignKey(EventSchedule, on_delete=models.PROTECT)
    key = models.CharField(max_length=255)
    value = models.TextField()
    memo = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.key}: {self.value}"
    

def doevents():
    event = EventSchedule.objects.filter(status=1).order_by("latestcalled_at")
    if event.exists():
        event.first().doevent()

def doevents_scheduler():
    if settings.TESTING:
        return
    import logging
    from apscheduler.schedulers.background import BackgroundScheduler

    logging.basicConfig()
    logging.getLogger('apscheduler').setLevel(logging.ERROR)

    scheduler = BackgroundScheduler()
    scheduler.add_job(doevents, 'interval', seconds=1)
    scheduler.start()


@receiver(request_started)
def database_initializer(*args, **kwargs):
    # print("database_initialize")
    schedules = EventSchedule.objects.filter(status=2)
    for schedule in schedules:
        schedule.status = 1
        schedule.save()

    # ログイン必要なサイトのドメインを登録
    domains = [".netkeiba.com"]
    for domain in domains:
        LoginForScraping.objects.get_or_create(domain=domain)

    # 新規レースID収集のイベントを登録
    category = EventCategory.objects.get_or_create(name="新しいレースIDを取得する")[0]
    category.use_method = "netkeiba.new_raceids"
    category.need_driver = True
    category.repeat = True
    category.save()
    schedule = EventSchedule.objects.get_or_create(title="新しいレースIDを取得する", category=category)[0]
    schedule.save()

    # 新規出馬表収集のイベントを登録
    category = EventCategory.objects.get_or_create(name="新しい出馬表を取得する")[0]
    category.use_method = "netkeiba.new_shutuba"
    category.need_driver = True
    category.page_load_strategy = "normal"
    category.repeat = True
    category.save()
    schedule = EventSchedule.objects.get_or_create(title="新しい出馬表を取得する", category=category)[0]
    schedule.save()

    


