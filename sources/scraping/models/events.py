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

class EventCategory(models.Model):
    name = models.CharField(max_length=255)
    use_method = models.CharField(max_length=255, default="test.default_methods")
    need_driver = models.BooleanField(default=False)
    page_load_strategy = models.CharField(max_length=255, default="eager")
    repeat = models.CharField(max_length=255, default="")
    # ','で区切り時間指定する。空白が指定されれば即実行する
    # date型が指定された場合はその日時にスケジューリングする
    # int型が指定された場合はその秒数後にスケジューリングする
    # - "" = 一度だけ実行
    # - "0:00:00" = 次の0時に実行
    # - "0:00:00," = 毎日0時に実行を繰り返す
    # - "0:00:00,12:00:00" = 毎日0時と12時に実行
    # - "0:00:00,12:00:00," = 毎日0時と12時に実行を繰り返す
    # - ",1,1,1" = 1秒ごとに3回実行
    # - "1,1,1" = 初回実行はスキップ、その後1秒ごとに3回実行
    # - "1,1,1," = 初回実行はスキップ、その後1秒ごとに3回実行を繰り返す
    # - ",1,1,1," = 1秒ごとに3回実行を繰り返す
    # - "0:00:00,1,1," = 毎日0時に1秒ごとに3回実行を繰り返す
    # - "0:00:00,1,1,1" = 毎日0時に1秒ごとに3回実行
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
        return f"{self.name}のイベントを実行しました。"

    def __str__(self):
        return self.name

class EventSchedule(models.Model):
    title = models.CharField(max_length=255)
    status = models.IntegerField(choices=[(i+1, s) for i, s in enumerate(["待機", "実行中", "完了", "エラー"])], default=1)
    startdatetime = models.DateTimeField(default=timezone.now)
    enddatetime = models.DateTimeField(null=True, blank=True)
    latestexecuted_at = models.DateTimeField(null=True, blank=True)
    latestcalled_at = models.DateTimeField(null=True, blank=True)
    errormessage = models.TextField(null=True, blank=True)
    category = models.ForeignKey(EventCategory, on_delete=models.PROTECT)
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
        
    def done(self):
        self.status = 3
        self.enddatetime = timezone.now()
        self.save()

    def doevent(self):
        self.latestcalled_at = timezone.now()
        self.save()
        if self.status == 2:
            return f"{self.title}は実行中です。"
        if self.status == 3:
            return f"{self.title}は既に完了しています。"
        if self.status == 4:
            return f"{self.title}はエラーが発生しています。"
        if self.startdatetime > timezone.now():
            return f"{self.title}はまだ実行できません。"
        if self.category.durationtime and self.latestexecuted_at and self.latestexecuted_at + timezone.timedelta(seconds=self.category.durationtime) > timezone.now():
            return f"{self.title}はまだ実行できません。"
        if self.enddatetime and self.enddatetime < timezone.now():
            return f"{self.title}は既に終了しています。"
        
        self.status = 2
        self.save()

        try:
            ret = self.category.doevent(**{d["key"]: d["value"] for d in self.eventargs_set.all().values()} if self.pk else {})
        except Exception as e:
            self.status = 4
            self.errormessage = f"{str(e)}\n{traceback.format_exc()}"
            self.save()
            raise e
        
        if self.category.repeat:
            self.status = 1
        else:
            self.status = 3

        self.latestexecuted_at = timezone.now()
        self.save()
        return ret

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
    category.durationtime = 60 * 60 * 24
    category.save()
    schedule = EventSchedule.objects.get_or_create(title="新しいレースIDを取得する", category=category)[0]
    schedule.save()

    # 新規出馬表収集のイベントを登録
    category = EventCategory.objects.get_or_create(name="新しい出馬表を取得する")[0]
    category.use_method = "netkeiba.new_shutuba"
    category.need_driver = True
    category.page_load_strategy = "normal"
    category.repeat = True
    category.durationtime = 180
    category.save()
    schedule = EventSchedule.objects.get_or_create(title="新しい出馬表を取得する", category=category)[0]
    schedule.save()

    


