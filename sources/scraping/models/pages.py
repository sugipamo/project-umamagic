from django.db import models

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
    race_id = models.OneToOneField(Race, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.race_id.race_id

    @staticmethod
    def get_unused_raceids():
        return Race.objects.exclude(shutuba__isnull=False)