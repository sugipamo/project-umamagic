from django.db import models
from apps.web_netkeiba_pagesources.models import Page

class NetkeibaRace(models.Model):
    race_id = models.CharField(max_length=255, verbose_name='レースID')
    page_source = models.ForeignKey(Page, on_delete=models.CASCADE, verbose_name='ページソース')