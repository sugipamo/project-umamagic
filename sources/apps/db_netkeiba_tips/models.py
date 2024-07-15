from django.db import models
from apps.web_netkeiba_pagesources.models import PageYoso, PageYosoCp, PageYosoPro
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from bs4 import BeautifulSoup as bs
import lxml.etree
from urllib.parse import urlparse, parse_qs
from django.utils import timezone
import datetime

class BaseHorseRacingTipParser(models.Model):
    need_update_at = models.DateTimeField(null=True, verbose_name='次回更新日時')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')

    class Meta:
        abstract = True

    @classmethod
    def next(cls, relate_model):
        unused_sources = relate_model.objects.exclude(page_ptr_id__in=cls.objects.values_list('page_source_id', flat=True))
        unused_source = unused_sources.order_by("created_at").first()
        if unused_source is not None:
            parser = cls(
                page_source = unused_source,
            )
            return parser
        
        return None

    def parser_init(self):
        self.need_update_at = timezone.now() + timezone.timedelta(days=1)
        
        soup = bs(self.page_source.read_html(), 'html.parser')
        etree = lxml.etree.HTML(str(soup))

        race_date = etree.xpath('//dd[@class="Active"]/a')
        if not race_date:
            return None
        race_date_href = race_date[0].get('href', "")
        
        parsed_url = urlparse(race_date_href)
        query_params = parse_qs(parsed_url.query)

        # Extract the kaisai_date
        kaisai_date = query_params.get('kaisai_date', [None])[0]

        if kaisai_date:
            self.need_update_at = timezone.make_aware(datetime.datetime.strptime(kaisai_date, "%Y%m%d")) + timezone.timedelta(days=1)

        self.save()
        return etree

    @classmethod
    def new_tip(cls):
        pass

class HorseRacingTipParserForPageYoso(BaseHorseRacingTipParser):
    page_source = models.ForeignKey(PageYoso, on_delete=models.CASCADE, verbose_name='取得元ページ')

    @classmethod
    def next(cls):
        return super().next(PageYoso)

    @classmethod
    def new_tip(cls):
        parser = cls.next()
        if not parser:
            return None
        
        etree = parser.parser_init()


class HorseRacingTipParserForPageYosoCp(BaseHorseRacingTipParser):
    page_source = models.ForeignKey(PageYosoCp, on_delete=models.CASCADE, verbose_name='取得元ページ')

class HorseRacingTipParserForPageYosoPro(BaseHorseRacingTipParser):
    page_source = models.ForeignKey(PageYosoPro, on_delete=models.CASCADE, verbose_name='取得元ページ')

class HorseRacingTipAuthor(models.Model):
    name = models.CharField(max_length=255, verbose_name='予想家名')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')

class HorseRacingTipMark(models.Model):
    mark = models.CharField(max_length=255, verbose_name='印')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')

class HorseRacingTip(models.Model):
    parser_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    parser_id = models.PositiveIntegerField()
    parser = GenericForeignKey('parser_type', 'parser_id')
    race_id = models.CharField(max_length=255, verbose_name='レースID')
    horse_number = models.IntegerField(verbose_name='馬番')
    mark = models.ForeignKey(HorseRacingTipMark, on_delete=models.CASCADE, verbose_name='印')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')
