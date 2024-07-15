from django.test import TestCase

from apps.db_netkeiba_tips.models import BaseHorseRacingTipParser, HorseRacingTipParserForPageYoso
from apps.web_netkeiba_pagesources.models import PageYoso
from django.utils import timezone
import datetime


class HorseRacingTipParserForPageYosoTest(TestCase):
    def test_new_tip(self):
        page_source = PageYoso.make_dummy_instance(category='nar', race_id='202444070902')
        self.assertTrue(HorseRacingTipParserForPageYoso(page_source=page_source).parser_init() is not None)
        HorseRacingTipParserForPageYoso.new_tip()
