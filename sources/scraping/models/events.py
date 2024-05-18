from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.signals import request_started
from django.dispatch import receiver
from scraping.model_utilitys.webdriver import WebDriver
from scraping.model_utilitys import event_methods
from scraping.models.login_for_scraping import LoginForScraping
import traceback

class ScheduleError(Exception):
    pass

class EventCategory(models.Model):
    name = models.CharField(max_length=255)
    use_method = models.CharField(max_length=255, default="test.default_methods")
    need_driver = models.BooleanField(default=False)
    page_load_strategy = models.CharField(max_length=255, default="eager")
    schedule_str = models.CharField(max_length=255, null=True, blank=True, default="0")
    parallel_limit = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
        return True

    def __str__(self):
        return self.name

class EventSchedule(models.Model):
    title = models.CharField(max_length=255)
    category = models.ForeignKey(EventCategory, on_delete=models.PROTECT)
    status = models.IntegerField(choices=[(i+1, s) for i, s in enumerate(["待機", "実行中", "完了", "エラー"])], default=1)
    nextexecutedatetime = models.DateTimeField(default=timezone.now)
    schedule_str = models.CharField(max_length=255, null=True, blank=True, default=",")
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
        if schedule_str is None:
            schedule_str = self.category.schedule_str
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
            raise ScheduleError(f"{self.title}は実行中です。")
        if self.status == 3:
            self.save()
            raise ScheduleError(f"{self.title}は既に完了しています。")
        if self.status == 4:
            self.save()
            raise ScheduleError(f"{self.title}はエラーが発生しています。")
        if not self.nextexecutedatetime is None and self.nextexecutedatetime > timezone.now():
            self.save()
            raise ScheduleError(f"{self.title}はまだ実行できません。")
        
        self.status = 2
        self.save()
        
        needdo, self.nextexecutedatetime, self.schedule_str = self.parse_schedule_str(self.schedule_str)
        if needdo:
            try:
                self.category.doevent(**{d["key"]: d["value"] for d in self.eventargs_set.all().values()} if self.pk else {})
            except Exception as e:
                self.status = 4
                self.errormessage = f"{str(e)}\n{traceback.format_exc()}"
                self.save()
                raise e
            
        if self.nextexecutedatetime is None:
            self.nextexecutedatetime = timezone.now()
            self.status = 3

        self.status = 1
        self.save()
        return needdo

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
    now = timezone.now()
    event = EventSchedule.objects.filter(status=1, nextexecutedatetime__lte=now).order_by("latestcalled_at")
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
    # schedules = EventSchedule.objects.filter(status=2)
    # for schedule in schedules:
    #     schedule.status = 1
    #     schedule.save()

    # ログイン必要なサイトのドメインを登録
    domains = [".netkeiba.com"]
    for domain in domains:
        LoginForScraping.objects.get_or_create(domain=domain)

    # 新規レースID収集のイベントを登録
    category = EventCategory.objects.get_or_create(name="新しいレースIDを取得する")[0]
    category.use_method = "netkeiba.new_raceids"
    category.need_driver = True
    category.schedule_str = str(60*60*24)+","
    category.save()
    schedule = EventSchedule.objects.get_or_create(title="新しいレースIDを取得する", category=category)[0]
    schedule.save()

    # ログイン不要の新規ページ収集のイベントを登録
    category = EventCategory.objects.get_or_create(name="ログイン不要のページを取得する")[0]
    category.use_method = "netkeiba.new_page"
    category.need_driver = True
    category.page_load_strategy = "normal"
    category.schedule_str = "0,0,0,0,0,0,0,0,0,0,0,0,0,0,360,0,0,0,0,0,3600,"
    category.save()
    schedule = EventSchedule.objects.get_or_create(title="ログイン不要のページを取得する", category=category)[0]
    schedule.save()

    # ログイン必要の新規ページ収集のイベントを登録
    category = EventCategory.objects.get_or_create(name="ログイン必要のページを取得する")[0]
    category.use_method = "netkeiba.new_page_with_login"
    category.need_driver = True
    category.page_load_strategy = "normal"
    category.schedule_str = "0,0,0,0,0,0,0,0,0,0,0,0,0,0,360,0,0,0,0,0,3600,"
    category.save()
    schedule = EventSchedule.objects.get_or_create(title="ログイン必要のページを取得する", category=category)[0]
    schedule.save()

    
    


