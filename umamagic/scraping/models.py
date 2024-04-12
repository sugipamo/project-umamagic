from django.db import models
import importlib
from django.utils import timezone
from .src.selenium import WebDriver

class EventCategory(models.Model):
    name = models.CharField(max_length=255)
    use_method = models.CharField(max_length=255, default="default_methods")
    need_driver = models.BooleanField(default=False)
    repeat = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def doevent(self, **kwargs):
        module = importlib.import_module(f"scraping.methods.{self.use_method}")
        method = getattr(module, "main")
        try:
            if self.need_driver:
                with WebDriver() as driver:
                    kwargs["driver"] = driver
                    method(**kwargs)
            else:
                method(**kwargs)
        except Exception as e:
            return e
        return f"{self.name}のイベントを実行しました。"

    def __str__(self):
        return self.name

class EventSchedule(models.Model):
    title = models.CharField(max_length=255)
    status = models.IntegerField(choices=[(i+1, s) for i, s in enumerate(["待機", "実行中", "完了", "エラー"])], default=1)
    startdatetime = models.DateTimeField(default=timezone.now)
    enddatetime = models.DateTimeField(null=True, blank=True)
    durationtime = models.IntegerField(null=True, blank=True)
    latestexecuted_at = models.DateTimeField(auto_now_add=True)
    errormessage = models.TextField(null=True, blank=True)
    category = models.ForeignKey(EventCategory, on_delete=models.PROTECT)
    memo = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.category.pk:
            self.category.save()
        super().save(*args, **kwargs)

    def __setitem__(self, key, value):
        self.save()
        try:
            eventargs = self.eventargs_set.get(key=key)
            eventargs.value = value
            eventargs.save()
        except:
            self.eventargs_set.create(key=key, value=value).save()

    def __getitem__(self, key):
        try:
            return self.eventargs_set.get(key=key).value
        except:
            return None
        
    def doevent(self):
        if self.status == 2:
            return f"{self.title}は実行中です。"
        elif self.status == 3:
            return f"{self.title}は既に実行済みです。"
        elif self.status == 4:
            return f"{self.title}はエラーが発生しています。"
        elif self.startdatetime > timezone.now():
            return f"{self.title}はまだ実行できません。"
        elif self.enddatetime and self.enddatetime < timezone.now():
            return f"{self.title}は既に終了しています。"

        self.status = 2
        self.save()

        ret = self.category.doevent(**{d["key"]: d["value"] for d in self.eventargs_set.all().values()} if self.pk else {})
        if isinstance(ret, Exception):
            self.status = 4
            self.errormessage = str(ret)
            self.save()
            return f"{self.category.name}のイベントを実行できませんでした。"
        
        if not self.category.repeat:
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