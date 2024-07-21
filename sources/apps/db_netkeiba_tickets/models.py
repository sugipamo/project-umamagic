from django.db import models
from django.utils import timezone
from bs4 import BeautifulSoup as bs
from urllib.parse import urlparse, parse_qs
import lxml
import datetime
from apps.web_netkeiba_pagesources.models import PageResult
from apps.web_netkeiba_pagesources.models import BasePageSourceParser

TICKET_NAMES = {
    "win": ["単勝"],
    "place": ["複勝"],
    "bracket_quinella": ["枠連"],
    "bracket_exacta": ["枠単"],
    "quinella": ["馬連"],
    "quinella_place": ["ワイド"],
    "exacta": ["馬単"],
    "trio": ["三連複", "3連複"],
    "trifecta": ["三連単", "3連単"],
}

TICKET_NAME_DICT = {
    **{name: name for name in TICKET_NAMES},
    **{ambiguous_name: name for name, ambiguous_names in TICKET_NAMES.items() for ambiguous_name in ambiguous_names}
}

TICKET_TYPES = {
    name: dict(zip(["horse_count", "length", "is_fixed", "is_bracket"], args)) 
    for name, args in {
        "win": (1, 1, True, False),
        "exacta": (2, 2, True, False),
        "trifecta": (3, 3, True, False),
        "quinella": (2, 2, False, False),
        "trio": (3, 3, False, False),
        "place": (1, 3, False, False),
        "quinella_place": (2, 3, False, False),
        "bracket_quinella": (2, 2, False, True),
        "bracket_exacta": (2, 2, True, True),
    }.items()
}


def win_str_replacer(win_str):
    replaces = [
        ('１', '1'), ('２', '2'), ('３', '3'), ('４', '4'), ('５', '5'),
        ('６', '6'), ('７', '7'), ('８', '8'), ('９', '9'), ('０', '0'),
        ('－', ' '), ('ー', ' '), ('―', ' '), ('→', ' '), ('　', ' '), ("-", " "),
    ]

    for u, v in replaces:
        win_str = win_str.replace(u, v)
    return win_str

class HorseRacingTicketParser(BasePageSourceParser):
    page_source = models.ForeignKey(PageResult, on_delete=models.CASCADE, verbose_name='取得元ページ')

    @classmethod
    def next(cls):
        return super().next(PageResult)

    def parser_init(self):
        self.need_update_at = timezone.now() + timezone.timedelta(days=1)
        
        html = self.page_source.read_html()
        if html is None:
            self.need_update_at = None
            self.save()
            return
        
        soup = bs(html, 'html.parser')
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
    def new_win_tickets(cls):
        parser = cls.next()
        if not parser:
            return None
        
        etree = parser.parser_init()

        if etree is None:
            return None

        result_pay_backs = etree.xpath('//table[@class="Payout_Detail_Table"]/tbody/tr')
        if not result_pay_backs:
            return None
        
        class NoElemsError(Exception):
            """Exception raised when there are no elements in the result_pay_back."""
            pass

        def get_elems(elem, xpath_str):
            """Get elements from the element by the xpath string."""
            elems = elem.xpath(xpath_str)
            if not elems:
                raise NoElemsError
            return elems
        
        tickets = []
        ticket_touchs = []
        for result_pay_back in result_pay_backs:
            try:
                ticket_name_elem = get_elems(result_pay_back, './th')[0]
                ticket_name = ticket_name_elem.text
                if ticket_name not in TICKET_NAME_DICT:
                    continue
                
                result_elem = get_elems(result_pay_back, './/td[@class="Result"]')[0]
                payout_elem = get_elems(result_pay_back, './/td[@class="Payout"]')[0]
                
                result_texts = [s.text for s in get_elems(result_elem, './/span')]
                result_texts = [t for t in result_texts if t]

                payout_raw_text = lxml.etree.tostring(payout_elem, encoding="utf-8").decode().replace("<br/>", "___")
                payout_texts = get_elems(lxml.etree.HTML(payout_raw_text), './/span')[0].text.split("___")
                payout_texts = [t.replace(",", "").replace("円", "") for t in payout_texts if t]

                ticket_horse_count = TICKET_TYPES[TICKET_NAME_DICT[ticket_name]]["horse_count"]
                for i, payout_text in enumerate(payout_texts):
                    win_str = " ".join(result_texts[i * ticket_horse_count:i * ticket_horse_count + ticket_horse_count])
                    ticket = HorseRacingTicket.from_win_str(
                        ticket_name, 
                        win_str, 
                        int(payout_text),
                        race_id=parser.page_source.race_id,
                        parser=parser,
                    )
                    tickets.append(ticket)
                    for j, horse_number in enumerate(map(int, win_str.split())): 
                        ticket_touch = HorseRacingTicketTouchNumber(
                            ticket=ticket,
                            horse_number=horse_number,
                            ticket_number_order=j+1
                        )
                        ticket_touchs.append(ticket_touch)


            except NoElemsError:
                continue



        if tickets:
            parser.need_update_at = None
            parser.success_parsing = True
            parser.save()
        for ticket in tickets:
            ticket.save()
        for ticket_touch in ticket_touchs:
            ticket_touch.save()

        return 
                

class HorseRacingTicketCompare():
    def __init__(self, ticket_name, *win_str):
        if ticket_name not in TICKET_NAME_DICT:
            raise ValueError(f"'{ticket_name}' is not recognized.")
        self.ticket_name = TICKET_NAME_DICT[ticket_name]
        ticket_type = TICKET_TYPES[self.ticket_name]
        self.horse_count = ticket_type["horse_count"]
        self.length = ticket_type["length"]
        self.is_fixed = ticket_type["is_fixed"]
        self.is_bracket = ticket_type["is_bracket"]

        if len(win_str) == 1 and type(win_str[0]) == str:
            win_nums = list(map(int, win_str_replacer(win_str[0]).split()))
        else:
            win_nums = list(map(int, win_str))

        if len(win_nums) < self.horse_count:
            raise ValueError(f"Invalid number of win numbers. Expected {self.length}, but got {len(win_nums)}.")
        self.win_nums = win_nums[:self.length]

    @classmethod
    def from_ticket_model(cls, ticket):
        return cls(ticket.official_name.name, ticket.win_str)
    
    def is_win(self, *race_results):
        """take a race result, and return whether this ticket is win or not."""


        if len(race_results) < self.length:
            raise ValueError(f"Invalid number of arguments. Expected {self.length}, but got {len(race_results)}.")
        
        if self.is_bracket:
            raise NotImplementedError("Bracket ticket is not supported yet.")
        
        if self.is_fixed:
            win_nums = list(self.win_nums)
            race_results_ = list(race_results[:self.length])
            while race_results_ and win_nums:
                r = race_results_.pop()
                w = win_nums.pop()
                if r != w:
                    win_nums.append(w)
            if win_nums:
                return False

        else:
            winset = set(self.win_nums)
            for i in race_results[:self.length]:
                if i in winset:
                    winset.remove(i)
            if winset:
                return False
            
        return True

    
    def __eq__(self, other):
        return self.ticket_name == other.ticket_name and self.win_nums == other.win_nums
    
    def __ne__(self, other):
        return not self.__eq__(other)

    def __contains__(self, other):
        if self.is_bracket or other.is_bracket:
            raise NotImplementedError("Bracket ticket is not supported yet.")

        raise NotImplementedError("This method is not implemented yet.")
    

class HorseRacingTicketName(models.Model):
    name = models.CharField(max_length=255, verbose_name='馬券名')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')

    def __str__(self):
        return self.name

class HorseRacingTicket(models.Model):
    parser = models.ForeignKey(HorseRacingTicketParser, on_delete=models.CASCADE, verbose_name='取得元')
    race_id = models.CharField(max_length=255, verbose_name='レースID')
    official_name = models.ForeignKey(HorseRacingTicketName, on_delete=models.CASCADE, verbose_name='馬券名')
    ambiguous_name = models.CharField(max_length=255, verbose_name='あいまいな馬券名')
    win_str = models.CharField(max_length=255, verbose_name='当選条件')
    refund = models.IntegerField(verbose_name='払戻金')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')

    def save(self):
        if self.refund <= 0:
            raise ValueError("Refund must be positive if you want to save this ticket.")
        super().save()

    def __str__(self):
        return f'{self.official_name} - {self.win_str} - {self.refund}'
    
    def is_win(self, *race_results):
        return HorseRacingTicketCompare.from_ticket_model(self).is_win(*race_results)

    @classmethod
    def from_win_str(cls, ticket_name, win_str, refund, **kwargs):
        ticket = cls(**kwargs)
        ticket.win_str = win_str_replacer(win_str)
        ticket.ambiguous_name = ticket_name
        if ticket.ambiguous_name not in TICKET_NAME_DICT:
            raise ValueError(f"'{ticket.ambiguous_name}' is not recognized.")
        official_name_key = TICKET_NAME_DICT.get(ticket.ambiguous_name)
        if len(ticket.win_str.split()) != TICKET_TYPES[official_name_key]["horse_count"]:
            raise ValueError(f"Invalid number of win numbers. Expected {TICKET_TYPES[official_name_key]['horse_count']}, but got {len(ticket.win_str.split())}.")

        ticket.official_name = HorseRacingTicketName.objects.get_or_create(name=official_name_key)[0]
        ticket.refund = refund

        return ticket
    

class HorseRacingTicketTouchNumber(models.Model):
    ticket = models.ForeignKey(HorseRacingTicket, on_delete=models.CASCADE, verbose_name='馬券')
    horse_number = models.IntegerField(verbose_name='馬番号')
    ticket_number_order = models.IntegerField(verbose_name='馬券内順序')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')

    def __str__(self):
        return f'{self.ticket} - {self.horse_number} - {self.ticket_number_order}'
    
    class Meta:
        unique_together = ('ticket', 'horse_number', 'ticket_number_order')
    
