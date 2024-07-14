from pathlib import Path
from django.test import TestCase
from unittest.mock import Mock
from .models import HorseRacingTicketParser
from .models import HorseRacingTicket, HorseRacingTicketName
from apps.web_netkeiba_pagesources.models import PageResult

class HorseRacingTicketParserTest(TestCase):
    def setUp(self):
        result = PageResult.make_dummy_instance(category='nar', race_id='202444070902')
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
    
    def test_make_bytelist(self):
        ticket = HorseRacingTicket()
        self.assertEqual(ticket._HorseRacingTicket__make_bytelist(1), 2)
        self.assertEqual(ticket._HorseRacingTicket__make_bytelist([0, 1, 2]), 7)
        self.assertEqual(ticket._HorseRacingTicket__make_bytelist("inf"), 1 << 21 - 1)
    
    def test_win_str_replacer(self):
        ticket = HorseRacingTicket()
        self.assertEqual(ticket._HorseRacingTicket__win_str_replacer('１－２－３'), '1 2 3')
        self.assertEqual(ticket._HorseRacingTicket__win_str_replacer('１ー２―３→４　５'), '1 2 3 4 5')
    
    def test_from_win_str_win(self):
        win_str = '１'
        ticket = HorseRacingTicket.from_win_str(ticket_name='単勝', win_str=win_str, refund=100, first=0, second=0, third=0)
        self.assertEqual(ticket.first, 1)
        self.assertEqual(ticket.second, 1 << 21 - 1)
        self.assertEqual(ticket.third, 1 << 21 - 1)
        self.assertEqual(ticket.refund, 100)
        self.assertEqual(ticket.official_name.name, 'win')

    def test_from_win_str_exacta(self):
        win_str = '１－２'
        ticket = HorseRacingTicket.from_win_str(ticket_name='馬単', win_str=win_str, refund=200, first=0, second=0, third=0)
        self.assertEqual(ticket.first, 1)
        self.assertEqual(ticket.second, 2)
        self.assertEqual(ticket.third, 1 << 21 - 1)
        self.assertEqual(ticket.refund, 200)
        self.assertEqual(ticket.official_name.name, 'exacta')

    def test_invalid_ticket_name(self):
        with self.assertRaises(ValueError):
            HorseRacingTicket.from_win_str(ticket_name='unknown', win_str='１－２', refund=200, first=0, second=0, third=0)

    def test_invalid_win_ticket_parts(self):
        with self.assertRaises(ValueError):
            HorseRacingTicket.from_win_str(ticket_name='単勝', win_str='１－２', refund=100, first=0, second=0, third=0)

    def test_invalid_exacta_ticket_parts(self):
        with self.assertRaises(ValueError):
            HorseRacingTicket.from_win_str(ticket_name='馬単', win_str='１', refund=200, first=0, second=0, third=0)
