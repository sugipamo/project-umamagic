from django.db import models
import gzip

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
    
    def read_html(self):
        return gzip.decompress(self.html).decode()

    def update_html(self, driver):
        driver.get(self.url)
        compressed_html = gzip.compress(driver.page_source.encode())
        self.html = compressed_html
        self.save()

    @classmethod
    def get_html_null_raceid(cls):
        return cls.objects.filter(html=None).first()
    
    @classmethod
    def get_unused_raceid(cls):
        # Get race_id that does not exist in Shutuba
        unused_race = Race.objects.exclude(race_id__in=cls.objects.values_list('race_id', flat=True)).order_by('created_at').first()
        if unused_race:
            # Create a new Shutuba object with the unused race_id
            new_shutuba = cls(race_id=unused_race.race_id, category=unused_race.category)
            return new_shutuba
        return None

class Shutuba(Race):
    html = models.BinaryField(null=True, blank=True)
    @property
    def url(self):
        return f"https://{self.category.name}/race/shutuba.html?race_id={self.race_id}"

# class RaceResult(Race):
#     html = models.BinaryField(null=True, blank=True)
#     @property
#     def url(self):
#         return f"https://{self.category.name}/race/result.html?race_id={self.race_id}"
    
