from django.db import models
from apps.web_netkeiba_pagesources.models import PageYoso, PageYosoCp, PageYosoPro
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class BaseHorseRacingTipParser(models.Model):
    page_source = models.ForeignKey(PageYoso, on_delete=models.CASCADE, verbose_name='取得元ページ')
    need_update_at = models.DateTimeField(null=True, verbose_name='次回更新日時')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')

    class Meta:
        abstract = True

    @classmethod
    def next(cls):
        unused_sources = cls.page_source.related_model.objects.exclude(
            page_ptr_id__in=cls.objects.values_list('page_source_id', flat=True)
        )
        unused_source = unused_sources.order_by("created_at").first()
        if unused_source is not None:
            parser = cls(
                page_source=unused_source,
            )
            return parser
        return None

class HorseRacingTipParserForPageYoso(BaseHorseRacingTipParser):
    page_source = models.ForeignKey(PageYoso, on_delete=models.CASCADE, verbose_name='取得元ページ')

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
