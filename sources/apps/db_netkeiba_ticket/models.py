from django.db import models
from apps.db_netkeiba_race.models import NetkeibaRace

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


class HorseRacingTicketName(models.Model):
    name = models.CharField(max_length=255, verbose_name='馬券名')
    description = models.TextField(verbose_name='説明')

    def __str__(self):
        return self.name

# ビット列で馬券を表現する
class HorseRacingTicket(models.Model):
    race = models.ForeignKey(NetkeibaRace, on_delete=models.CASCADE, verbose_name='レース')
    official_name = models.ForeignKey(HorseRacingTicketName, on_delete=models.CASCADE, verbose_name='馬券名')
    ambiguous_name = models.CharField(max_length=255, verbose_name='あいまいな馬券名')
    win_str = models.CharField(max_length=255, verbose_name='当選条件')
    first = models.IntegerField(verbose_name='1着')
    second = models.IntegerField(verbose_name='2着')
    third = models.IntegerField(verbose_name='3着')
    refund = models.IntegerField(verbose_name='払戻金')

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
    

