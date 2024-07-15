from django.test import TestCase
from .models import HorseRacingTicketParser
from .models import HorseRacingTicket, HorseRacingTicketName
from apps.web_netkeiba_pagesources.models import PageResult
from .models import win_str_replacer
from .models import HorseRacingTicketCompare

class HorseRacingTicketCompareTest(TestCase):
    def setUp(self):
        self.win_name = HorseRacingTicketName.objects.create(name='win')
        self.exacta_name = HorseRacingTicketName.objects.create(name='exacta')
        self.win_ticket = HorseRacingTicket(
            official_name=self.win_name,
            refund=100,
            win_str="1"
        )
        self.exacta_ticket = HorseRacingTicket(
            official_name=self.exacta_name,
            refund=200,
            win_str="1 2"
        )

    def test_is_win(self):
        self.assertTrue(self.win_ticket.is_win(1))
        self.assertFalse(self.win_ticket.is_win(2))
        self.assertTrue(self.exacta_ticket.is_win(1, 2))
        self.assertFalse(self.exacta_ticket.is_win(2, 1))

    def test_from_ticket_model(self):
        ticket_cmp = HorseRacingTicketCompare
        self.assertTrue(ticket_cmp.from_ticket_model(self.win_ticket) == ticket_cmp.from_ticket_model(self.win_ticket))
        self.assertFalse(ticket_cmp.from_ticket_model(self.win_ticket) == ticket_cmp.from_ticket_model(self.exacta_ticket))

    def test_from_ticket_model_invalid(self):
        with self.assertRaises(TypeError):
            HorseRacingTicketCompare.from_ticket_model(self.win_ticket, self.exacta_ticket)

    def test_win_ticket(self):
        self.assertTrue(HorseRacingTicketCompare("win", 1).is_win(1))
        self.assertFalse(HorseRacingTicketCompare("win", 1).is_win(2))
        
    def test_exacta_ticket(self):
        self.assertTrue(HorseRacingTicketCompare("exacta", 1, 2).is_win(1, 2))
        self.assertFalse(HorseRacingTicketCompare("exacta", 1, 2).is_win(2, 1))

    def test_trifecta_ticket(self):
        self.assertTrue(HorseRacingTicketCompare("trifecta", 1, 2, 3).is_win(1, 2, 3))
        self.assertFalse(HorseRacingTicketCompare("trifecta", 1, 2, 3).is_win(3, 2, 1))

    def test_quinella_ticket(self):
        self.assertTrue(HorseRacingTicketCompare("quinella", 1, 2).is_win(1, 2))
        self.assertTrue(HorseRacingTicketCompare("quinella", 1, 2).is_win(2, 1))
        self.assertFalse(HorseRacingTicketCompare("quinella", 1, 2).is_win(3, 1))

    def test_trio_ticket(self):
        self.assertTrue(HorseRacingTicketCompare("trio", 1, 2, 3).is_win(1, 2, 3))
        self.assertTrue(HorseRacingTicketCompare("trio", 1, 2, 3).is_win(3, 2, 1))
        self.assertTrue(HorseRacingTicketCompare("trio", 1, 2, 3).is_win(2, 3, 1))
        self.assertFalse(HorseRacingTicketCompare("trio", 1, 2, 3).is_win(3, 2, 4))

    def test_place_ticket(self):
        self.assertTrue(HorseRacingTicketCompare("place", 1).is_win(1, 2, 3))
        self.assertFalse(HorseRacingTicketCompare("place", 1).is_win(2, 3, 4))
        self.assertFalse(HorseRacingTicketCompare("place", 1).is_win(3, 4, 5))
        self.assertFalse(HorseRacingTicketCompare("place", 1).is_win(4, 5, 6))

    def test_quinella_place_ticket(self):
        self.assertTrue(HorseRacingTicketCompare("quinella_place", 1, 2).is_win(1, 2, 3))
        self.assertTrue(HorseRacingTicketCompare("quinella_place", 1, 2).is_win(2, 1, 3))
        self.assertFalse(HorseRacingTicketCompare("quinella_place", 1, 2).is_win(1, 3, 4))
        self.assertFalse(HorseRacingTicketCompare("quinella_place", 1, 2).is_win(4, 5, 6))

    def test_bracket_quinella_ticket(self):
        with self.assertRaises(NotImplementedError):
            HorseRacingTicketCompare("bracket_quinella", 1, 2).is_win(1, 2)

    def test_bracket_exacta_ticket(self):
        with self.assertRaises(NotImplementedError):
            HorseRacingTicketCompare("bracket_exacta", 1, 2).is_win(1, 2)

class WinStrReplacerTest(TestCase):
    def test_win_str_replacer(self):
        self.assertEqual(win_str_replacer('１－２－３'), '1 2 3')
        self.assertEqual(win_str_replacer('１ー２―３→４　５'), '1 2 3 4 5')

class HorseRacingTicketNarParserTest(TestCase):
    def setUp(self):
        result = PageResult.make_dummy_instance(category='nar', race_id='202444070902')
        self.parser = HorseRacingTicketParser(page_source=result)
        
    def test_parser_parser_init(self):
        self.assertTrue(self.parser._HorseRacingTicketParser__parser_init() is not None)

    def test_new_win_tickets(self):
        HorseRacingTicketParser.new_win_tickets()
        self.assertTrue(HorseRacingTicket.objects.all().exists())

class HorseRacingTicketRaceParserTest(TestCase):
    def setUp(self):
        result = PageResult.make_dummy_instance(category='race', race_id='202402010911')
        self.parser = HorseRacingTicketParser(page_source=result)
        
    def test_parser_parser_init(self):
        self.assertTrue(self.parser._HorseRacingTicketParser__parser_init() is not None)

    def test_new_win_tickets(self):
        HorseRacingTicketParser.new_win_tickets()
        self.assertTrue(HorseRacingTicket.objects.all().exists())

class HorseRacingTicketNameTest(TestCase):
    def test_str(self):
        ticket_name = HorseRacingTicketName.objects.create(name='Win')
        self.assertEqual(str(ticket_name), 'Win')

class HorseRacingTicketTest(TestCase):
    def setUp(self):
        self.win_name = HorseRacingTicketName.objects.create(name='win')
        self.exacta_name = HorseRacingTicketName.objects.create(name='exacta')
    
    def test_from_win_str_win(self):
        win_str = '１'
        ticket = HorseRacingTicket.from_win_str(ticket_name='単勝', win_str=win_str, refund=100)
        self.assertEqual(ticket.refund, 100)
        self.assertEqual(ticket.official_name.name, 'win')

    def test_from_win_str_exacta(self):
        win_str = '１－２'
        ticket = HorseRacingTicket.from_win_str(ticket_name='馬単', win_str=win_str, refund=200)
        self.assertEqual(ticket.refund, 200)
        self.assertEqual(ticket.official_name.name, 'exacta')

    def test_invalid_ticket_name(self):
        with self.assertRaises(ValueError):
            HorseRacingTicket.from_win_str(ticket_name='unknown', win_str='１－２', refund=200)

    def test_invalid_win_ticket_parts(self):
        with self.assertRaises(ValueError):
            HorseRacingTicket.from_win_str(ticket_name='単勝', win_str='１－２', refund=100)

    def test_invalid_exacta_ticket_parts(self):
        with self.assertRaises(ValueError):
            HorseRacingTicket.from_win_str(ticket_name='馬単', win_str='１', refund=200)
