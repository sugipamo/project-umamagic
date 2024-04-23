from django.db import models
from django.utils import timezone
from .webdriver import WebDriver
from . import event_methods
from apscheduler.schedulers.background import BackgroundScheduler

class EventCategory(models.Model):
    name = models.CharField(max_length=255)
    use_method = models.CharField(max_length=255, default="Test.default_methods")
    need_driver = models.BooleanField(default=False)
    repeat = models.BooleanField(default=False)
    parallel_limit = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def doevent(self, **kwargs):
        method = event_methods
        for s in self.use_method.split("."):
            method = getattr(method, s)
        if self.need_driver:                
            with WebDriver() as driver:
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
    durationtime = models.IntegerField(null=True, blank=True)
    latestexecuted_at = models.DateTimeField(default=timezone.now)
    latestcalled_at = models.DateTimeField(default=timezone.now)
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
        if self.status == 2:
            return f"{self.title}は実行中です。"
        if self.status == 3:
            return f"{self.title}は既に完了しています。"
        if self.status == 4:
            return f"{self.title}はエラーが発生しています。"
        if self.startdatetime > timezone.now():
            return f"{self.title}はまだ実行できません。"
        if self.durationtime and self.latestexecuted_at and self.latestexecuted_at + timezone.timedelta(seconds=self.durationtime) > timezone.now():
            return f"{self.title}はまだ実行できません。"
        if self.enddatetime and self.enddatetime < timezone.now():
            return f"{self.title}は既に終了しています。"

        self.latestexecuted_at = timezone.now()
        self.status = 2
        self.save()

        try:
            ret = self.category.doevent(**{d["key"]: d["value"] for d in self.eventargs_set.all().values()} if self.pk else {})
        except Exception as e:
            self.status = 4
            self.errormessage = str(e)
            self.save()
            raise e
        
        if self.category.repeat:
            self.status = 1
        else:
            self.status = 3

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
    from django.conf import settings
    if settings.TESTING:
        return
    scheduler = BackgroundScheduler()
    scheduler.add_job(doevents, 'interval', seconds=1)
    scheduler.start()