from django.db import models
from django.db.models import Q
import gzip

class NonUrlError(Exception):
    pass

class PageCategory(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Page(models.Model):
    race_id = models.CharField(max_length=255)
    category = models.ForeignKey(PageCategory, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.race_id
    
    def read_html(self):
        return gzip.decompress(self.html).decode()

    def update_html(self, driver):
        driver.get(self.url)
        self.html = gzip.compress(driver.page_source.encode())
        self.save_base(raw=True)

    @classmethod
    def next_raceid(cls):
        shutuba = cls.objects.filter(html=None).first()
        if shutuba is not None:
            return shutuba

        unused_races = Page.objects.exclude(race_id__in=cls.objects.values_list('race_id', flat=True))
        unused_races = unused_races.filter(
            Q(category__name="nar.netkeiba.com") |
            Q(category__name="race.netkeiba.com")
        )
        unused_race = unused_races.order_by("created_at").first()
        if unused_race:
            shutuba = cls(page_ptr=unused_race)
            return shutuba

        return None


class PageShutuba(Page):
    html = models.BinaryField(null=True, blank=True)
    @property
    def url(self):
        return f"https://{self.page_ptr.category.name}/race/shutuba.html?race_id={self.page_ptr.race_id}"

class PageResult(Page):
    html = models.BinaryField(null=True, blank=True)
    @property
    def url(self):
        return f"https://{self.page_ptr.category.name}/race/result.html?race_id={self.page_ptr.race_id}"
    
class PageDbNetkeiba(Page):
    html = models.BinaryField(null=True, blank=True)
    @property
    def url(self):
        return f"https://db.netkeiba.com/race/{self.page_ptr.race_id}"