from django.db import models

# Create your models here.

class ScrapeCategory(models.Model):
    name = models.CharField(max_length=255)
    use_method = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class CrawlSchedule(models.Model):
    title = models.CharField(max_length=255)
    url = models.URLField()
    category = models.ForeignKey(ScrapeCategory, on_delete=models.CASCADE)
    memo = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日")
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name="削除日")

    def __str__(self):
        return self.title