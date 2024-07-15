from django.db import models
from apps.web_netkeiba_pagesources.models import PageYoso, PageYosoCp, PageYosoPro
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from bs4 import BeautifulSoup as bs
import lxml.etree
from urllib.parse import urlparse, parse_qs
from django.utils import timezone
import datetime


MARKS = {
    "First": ["◎", "Icon_Shirushi Icon_Honmei", "Icon_Shirushi Icon_Shirushi1"],
    "Second": ["〇", "○", "Icon_Shirushi Icon_Taikou", "Icon_Shirushi Icon_Shirushi2"],
    "Third": ["▲", "Icon_Shirushi Icon_Kurosan", "Icon_Shirushi Icon_Shirushi3"],
    "Fourth": ["△", "Icon_Shirushi Icon_Osae", "Icon_Shirushi Icon_Shirushi4"],
    "Star": ["☆", "Icon_Shirushi Icon_Hoshi"],
}

MARKS = {
    **{name: name for name in MARKS},
    **{mark: name for name, marks in MARKS.items() for mark in marks},
}

class BaseHorseRacingTipParser(models.Model):
    need_update_at = models.DateTimeField(null=True, verbose_name='次回更新日時')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')

    class Meta:
        abstract = True

    @classmethod
    def next(cls, relate_model):
        unupdated_parsers = cls.objects.filter(need_update_at__lte=timezone.now())
        unupdated_parser = unupdated_parsers.order_by("need_update_at").first()
        if unupdated_parser is not None:
            return unupdated_parser

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
        etree = lxml.etree.HTML(str(soup).replace("<br/>", "").replace("<br>", "").replace("<br />", ""))

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
    def new_tips(cls):
        parser = cls.next()
        if not parser:
            return None
        
        etree = parser.parser_init()

        if etree is None:
            return None
        
        yoso_table_wrap = etree.xpath("//div[@class='YosoTableWrap']")
        if not yoso_table_wrap:
            return None
        
        tips = []
        
        for yosoka in yoso_table_wrap[0].xpath(".//dl[@class='Yosoka']"):
            yosoka_name = yosoka.xpath(".//p[@class='yosoka_name']")[0].text
            for i, icon in enumerate(yosoka.xpath(".//li/span")):
                icon_name = icon.attrib.get('class', "")
                if icon_name not in MARKS:
                    continue
                mark = MARKS[icon_name]
                horse_number = i + 1
                tip = HorseRacingTip(
                    parser = parser,
                    race_id = parser.page_source.race_id,
                    horse_number = horse_number,
                    author = HorseRacingTipAuthor.objects.get_or_create(name=yosoka_name)[0],
                    mark = HorseRacingTipMark.objects.get_or_create(mark=mark)[0],
                )
                tips.append(tip)

        if tips:
            parser.need_update_at = None
            parser.save()
        for tip in tips:
            tip.save()

        return tips

class HorseRacingTipParserForPageYosoCp(BaseHorseRacingTipParser):
    page_source = models.ForeignKey(PageYosoCp, on_delete=models.CASCADE, verbose_name='取得元ページ')

    @classmethod
    def next(cls):
        return super().next(PageYosoCp)
    
    def parser_init(self):
        self.need_update_at = timezone.now() + timezone.timedelta(days=1)
        
        soups = {name: bs(source, 'html.parser') for name, source in self.page_source.read_html().items()}
        etrees = {name: lxml.etree.HTML(str(soup).replace("<br/>", "").replace("<br>", "").replace("<br />", "")) for name, soup in soups.items()}
        etree = list(etrees.values())[0]

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
        return etrees

    @classmethod
    def new_tips(cls):
        parser = cls.next()
        if not parser:
            return None
        
        etrees = parser.parser_init()

        if etrees is None:
            return None
        
        tips = []

        first_run = True
        
        for cp_name, etree in etrees.items():
            cp_name = cp_name
            horse_data_table = etree.xpath("//table[@id='YosoMarkTable01']")
            if not horse_data_table:
                continue
            horse_data_table = horse_data_table[0]

            if first_run:
                headers = horse_data_table.xpath("./thead/tr[@class='CP_Result']/th")
                headers = [h for h in headers if len(h.attrib) == 0]
                def extract_text(h):
                    text = h.text
                    if text is None:
                        div = h.xpath(".//div")
                        if div:
                            text = div[0].text
                    if text is None:
                        text = ""
                    return text
                headers = [extract_text(h) for h in headers]

                cp_results_tr = horse_data_table.xpath("./tbody/tr[@class='CP_Result']")
                cp_results_td = [cp_result.xpath(".//td[@class='Mark_Pro']") for cp_result in cp_results_tr]
                def extract_span(cp):
                    span = cp.xpath(".//span")
                    if not span:
                        return ""
                    mark = span[0].attrib.get('class', "")
                    if mark not in MARKS:
                        return ""
                    return MARKS[mark]

                cp_results = [[extract_span(cp) for cp in cp_result] for cp_result in cp_results_td]

                for i in range(len(cp_results)):
                    for j in range(-len(headers), 0, 1):
                        mark = cp_results[i][j]
                        if mark not in MARKS:
                            continue
                        horse_number = i + 1
                        tip = HorseRacingTip(
                            parser = parser,
                            race_id = parser.page_source.race_id,
                            horse_number = horse_number,
                            author = HorseRacingTipAuthor.objects.get_or_create(name=headers[j])[0],
                            mark = HorseRacingTipMark.objects.get_or_create(mark=mark)[0],
                        )
                        tips.append(tip)

                first_run = False

            for i, cp_result in enumerate(horse_data_table.xpath("./tbody/tr[@class='CP_Result']")):
                horse_number = i + 1
                mark_td = cp_result.xpath(".//td[@class='Mark_Pro']")
                if not mark_td:
                    continue
                mark_span = mark_td[0].xpath(".//span")
                if not mark_span:
                    continue
                mark = mark_span[0].attrib.get('class', "")
                if mark not in MARKS:
                    continue

                mark = MARKS[mark]
                tip = HorseRacingTip(
                    parser = parser,
                    race_id = parser.page_source.race_id,
                    horse_number = horse_number,
                    author = HorseRacingTipAuthor.objects.get_or_create(name=cp_name)[0],
                    mark = HorseRacingTipMark.objects.get_or_create(mark=mark)[0],
                )
                tips.append(tip)
                print(f'check_values("{tip.race_id}", "{tip.author.name}", {tip.horse_number}, "{tip.mark.mark}")')


        if tips:
            parser.need_update_at = None
            parser.save()
        for tip in tips:
            tip.save()

        return tips

class HorseRacingTipParserForPageYosoPro(BaseHorseRacingTipParser):
    page_source = models.ForeignKey(PageYosoPro, on_delete=models.CASCADE, verbose_name='取得元ページ')

    @classmethod
    def next(cls):
        return super().next(PageYosoPro)

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
    author = models.ForeignKey(HorseRacingTipAuthor, on_delete=models.CASCADE, verbose_name='予想家')
    mark = models.ForeignKey(HorseRacingTipMark, on_delete=models.CASCADE, verbose_name='印')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')

    def __str__(self):
        return f"{self.race_id} {self.author.name} {self.horse_number} {self.mark.mark}"