from django.db import models
from scraping.model_utilitys.webdriver import TimeCounter

class RaceCategory(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Race(models.Model):
    race_id = models.CharField(max_length=255)
    category = models.ForeignKey(RaceCategory, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.race_id

class Shutuba(models.Model):
    race = models.OneToOneField(Race, on_delete=models.PROTECT)
    html = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.race.race_id

    @staticmethod
    def get_unused_raceids():
        return Race.objects.exclude(shutuba__isnull=False)
    
    @property
    def url(self):
        return f"https://{self.race.category.name}/race/shutuba.html?race_id={self.race.race_id}"

    def update_html(self, driver):
        driver.get(self.url)
        with TimeCounter() as tc:
            tc.do(driver.find_element, "xpath", ".//table")
        self.html = driver.page_source
        self.save()