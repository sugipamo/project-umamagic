from django.db import models
from django.utils import timezone
from bs4 import BeautifulSoup as bs
import lxml
from apps.web_netkeiba_pagesources.models import PageResult

# Define the ambiguous names and their corresponding official names
TICKET_NAMES = {
    "win": ["単勝"],
    "place": ["複勝"],
    "bracket_quinella": ["枠連"],
    "quinella": ["馬連"],
    "quinella_place": ["ワイド"],
    "exacta": ["馬単"],
    "trio": ["三連複", "3連複"],
    "trifecta": ["三連単", "3連単"],
}

# Create a dictionary to map ambiguous names to official names
TICKET_NAME_DICT = {ambiguous_name: name for name, ambiguous_names in TICKET_NAMES.items() for ambiguous_name in ambiguous_names}


class HorseRacingTicketParser(models.Model):
    page_source = models.ForeignKey(PageResult, on_delete=models.CASCADE, verbose_name='取得元ページ')
    need_update_at = models.DateTimeField(null=True, verbose_name='次回更新日時')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')

    @classmethod
    def next(cls):
        unused_sources = PageResult.objects.exclude(race_id__in=cls.objects.values_list('race_id', flat=True))
        unused_source = unused_sources.order_by("created_at").first()
        if unused_source:
            parser = cls(
                page_source = unused_source,
            )
            return parser
        
        return None

    def __parser_init(self):
        self.need_update_at = timezone.now() + timezone.timedelta(days=1)
        
        soup = bs(self.page_source.read_html(), 'html.parser')
        etree = lxml.etree.HTML(str(soup))

        race_date = etree.xpath('//dd[@class="Active"]/a')
        if not race_date:
            return None
        
        race_date_href = race_date.get('href', "")
        race_date_split = race_date_href.split("?")
        if len(race_date_split) < 2:
            return None
        race_date_params = race_date_split[1].split("&")
        kaisai_date = {k: v for race_date_param in race_date_params for k, v in race_date_param.split("=")}
        kaisai_date = kaisai_date.get("kaisai_date", "")
        if not kaisai_date:
            return None
        
        need_update_at = timezone.datetime.strptime(kaisai_date, "%Y%m%d") + timezone.timedelta(days=1)
        self.need_update_at = need_update_at

        return etree

    @classmethod
    def new_win_tickets(cls):
        parser = cls.next()
        if not parser:
            return None
        
        etree = parser.__parser_init()

        ResultPayBackWrapper = etree.xpath('//div[@class="ResultPayBackWrapper"]')
        if not ResultPayBackWrapper:
            return None
        
        


class HorseRacingTicketName(models.Model):
    name = models.CharField(max_length=255, verbose_name='馬券名')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')

    def __str__(self):
        return self.name

# ビット列で馬券的中範囲を表現する
class HorseRacingTicket(models.Model):
    parser = models.ForeignKey(HorseRacingTicketParser, on_delete=models.CASCADE, verbose_name='取得元')
    race_id = models.CharField(max_length=255, verbose_name='レースID')
    official_name = models.ForeignKey(HorseRacingTicketName, on_delete=models.CASCADE, verbose_name='馬券名')
    ambiguous_name = models.CharField(max_length=255, verbose_name='あいまいな馬券名')
    win_str = models.CharField(max_length=255, verbose_name='当選条件')
    first = models.IntegerField(verbose_name='1着')
    second = models.IntegerField(verbose_name='2着')
    third = models.IntegerField(verbose_name='3着')
    refund = models.IntegerField(verbose_name='払戻金')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')

    def save(self):
        if self.refund <= 0:
            raise ValueError("Refund must be positive if you want to save this ticket.")
        super().save()

    def __str__(self):
        return f'{self.official_name}-{self.win_str}'

    def __contains__(self, other):
        for me, you in zip([self.first, self.second, self.third], [other.first, other.second, other.third]):
            if me & you != you:
                return False
        return True

    def __make_bytelist(self, nums):
        if nums == "inf":
            return 1 << 21 - 1
        if type(nums) is int:
            nums = [nums]

        num = 0
        for n in nums:
            num |= 1 << n
        return num


    def __win_str_replacer(self, win_str):
        replaces = [
            ('１', '1'), ('２', '2'), ('３', '3'), ('４', '4'), ('５', '5'),
            ('６', '6'), ('７', '7'), ('８', '8'), ('９', '9'), ('０', '0'),
            ('－', ' '), ('ー', ' '), ('―', ' '), ('→', ' '), ('　', ' '), ("-", " "),
        ]

        for u, v in replaces:
            win_str = win_str.replace(u, v)
        return win_str

    @classmethod
    def from_win_str(cls, ticket_name, win_str, refund, **kwargs):
        ticket = cls(**kwargs)
        parts = ticket.__win_str_replacer(win_str).split()
        ticket.ambiguous_name, parts = ticket_name, [int(part) - 1 for part in parts]
        official_name_key = TICKET_NAME_DICT.get(ticket.ambiguous_name)
        if not official_name_key:
            raise ValueError(f"'{ticket.ambiguous_name}' is not recognized.")
        ticket.official_name = HorseRacingTicketName.objects.get_or_create(name=official_name_key)[0]
        ticket.refund = refund

        if "win" == official_name_key:
            if len(parts) != 1:
                raise ValueError("Win ticket must have only one part.")
            ticket.first = ticket.__make_bytelist(parts)
            ticket.second = ticket.__make_bytelist("inf")
            ticket.third = ticket.__make_bytelist("inf")

        elif "place" == official_name_key:
            raise ValueError("Place ticket is not supported.")
        
        elif "bracket_quinella" == official_name_key:
            raise ValueError("Bracket quinella ticket is not supported.")

        elif "quinella_place" == official_name_key:
            raise ValueError("Quinella place ticket is not supported.")
        
        elif "quinella" == official_name_key:
            if len(parts) != 2:
                raise ValueError("Quinella ticket must have two parts.")
            ticket.first = ticket.__make_bytelist(parts)
            ticket.second = ticket.__make_bytelist(parts)
            ticket.third = ticket.__make_bytelist("inf")

        elif "exacta" == official_name_key:
            if len(parts) != 2:
                raise ValueError("Exacta ticket must have two parts.")
            ticket.first = ticket.__make_bytelist(parts[0])
            ticket.second = ticket.__make_bytelist(parts[1])
            ticket.third = ticket.__make_bytelist("inf")

        elif "trio" == official_name_key:
            if len(parts) != 3:
                raise ValueError("Trio ticket must have three parts.")
            ticket.first = ticket.__make_bytelist(parts)
            ticket.second = ticket.__make_bytelist(parts)
            ticket.third = ticket.__make_bytelist(parts)

        elif "trifecta" == official_name_key:
            if len(parts) != 3:
                raise ValueError("Trifecta ticket must have three parts.")
            ticket.first = ticket.__make_bytelist(parts[0])
            ticket.second = ticket.__make_bytelist(parts[1])
            ticket.third = ticket.__make_bytelist(parts[2])
        
        return ticket