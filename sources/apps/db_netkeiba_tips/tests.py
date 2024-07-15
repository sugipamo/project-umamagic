from django.test import TestCase

from apps.db_netkeiba_tips.models import HorseRacingTipParserForPageYoso, HorseRacingTipParserForPageYosoCp
from apps.db_netkeiba_tips.models import HorseRacingTip
from apps.web_netkeiba_pagesources.models import PageYoso, PageYosoCp


class HorseRacingTipParserForPageYosoCPNarTest(TestCase):
    def test_new_tips(self):
        page_source = PageYosoCp.make_dummy_instance(category='nar', race_id='202444070902')
        self.assertTrue(HorseRacingTipParserForPageYosoCp(page_source=page_source).parser_init() is not None)
        HorseRacingTipParserForPageYosoCp.objects.all().delete()
        HorseRacingTipParserForPageYosoCp.new_tips()
        self.assertTrue(HorseRacingTipParserForPageYosoCp.objects.all().exists())


class HorseRacingTipParserForPageYosoCPRaceTest(TestCase):
    def test_new_tips(self):
        page_source = PageYosoCp.make_dummy_instance(category='race', race_id='202408040811')
        self.assertTrue(HorseRacingTipParserForPageYosoCp(page_source=page_source).parser_init() is not None)
        HorseRacingTipParserForPageYosoCp.objects.all().delete()
        HorseRacingTipParserForPageYosoCp.new_tips()
        self.assertTrue(HorseRacingTipParserForPageYosoCp.objects.all().exists())



class HorseRacingTipParserForPageYosoNarTest(TestCase):
    def test_new_tips(self):
        page_source = PageYoso.make_dummy_instance(category='nar', race_id='202444070902')
        self.assertTrue(HorseRacingTipParserForPageYoso(page_source=page_source).parser_init() is not None)
        HorseRacingTipParserForPageYoso.objects.all().delete()
        HorseRacingTipParserForPageYoso.new_tips()
        self.assertTrue(HorseRacingTipParserForPageYoso.objects.all().exists())

        def check_values(race_id, author, horse_number, mark):
            tip = HorseRacingTip.objects.get(author__name=author, horse_number=horse_number)
            self.assertTrue(tip.race_id == "202444070902")
            self.assertTrue(tip.author.name == author)
            self.assertTrue(tip.horse_number == horse_number)
            self.assertTrue(tip.mark.mark == mark)

        check_values("202444070902", "浅野", 1, "Fourth")
        check_values("202444070902", "浅野", 3, "Second")
        check_values("202444070902", "浅野", 8, "Star")
        check_values("202444070902", "浅野", 12, "Third")
        check_values("202444070902", "浅野", 13, "First")
        check_values("202444070902", "CP予想", 3, "Third")
        check_values("202444070902", "CP予想", 5, "Second")
        check_values("202444070902", "CP予想", 8, "Fourth")
        check_values("202444070902", "CP予想", 13, "First")


class HorseRacingTipParserForPageYosoRaceTest(TestCase):
    def test_new_tips(self):
        page_source = PageYoso.make_dummy_instance(category='race', race_id='202408040811')
        self.assertTrue(HorseRacingTipParserForPageYoso(page_source=page_source).parser_init() is not None)
        HorseRacingTipParserForPageYoso.objects.all().delete()
        HorseRacingTipParserForPageYoso.new_tips()
        self.assertTrue(HorseRacingTipParserForPageYoso.objects.all().exists())

        def check_values(race_id, author, horse_number, mark):
            tip = HorseRacingTip.objects.get(author__name=author, horse_number=horse_number)
            self.assertTrue(tip.race_id == race_id)
            self.assertTrue(tip.author.name == author)
            self.assertTrue(tip.horse_number == horse_number)
            self.assertTrue(tip.mark.mark == mark)

        check_values("202408040811", "本紙", 1, "Star")
        check_values("202408040811", "本紙", 2, "Fourth")
        check_values("202408040811", "本紙", 5, "Third")
        check_values("202408040811", "本紙", 7, "Second")
        check_values("202408040811", "本紙", 9, "Fourth")
        check_values("202408040811", "本紙", 10, "Fourth")
        check_values("202408040811", "本紙", 12, "First")
        check_values("202408040811", "須田", 1, "Fourth")
        check_values("202408040811", "須田", 2, "Star")
        check_values("202408040811", "須田", 3, "Fourth")
        check_values("202408040811", "須田", 4, "Fourth")
        check_values("202408040811", "須田", 7, "First")
        check_values("202408040811", "須田", 10, "Second")
        check_values("202408040811", "須田", 11, "Fourth")
        check_values("202408040811", "須田", 12, "Third")
        check_values("202408040811", "丹下", 1, "Fourth")
        check_values("202408040811", "丹下", 2, "Second")
        check_values("202408040811", "丹下", 3, "Star")
        check_values("202408040811", "丹下", 4, "First")
        check_values("202408040811", "丹下", 10, "Fourth")
        check_values("202408040811", "丹下", 12, "Third")
        check_values("202408040811", "丹下", 13, "Fourth")
        check_values("202408040811", "田沼", 2, "Fourth")
        check_values("202408040811", "田沼", 3, "Second")
        check_values("202408040811", "田沼", 4, "Third")
        check_values("202408040811", "田沼", 7, "Fourth")
        check_values("202408040811", "田沼", 9, "Star")
        check_values("202408040811", "田沼", 10, "First")
        check_values("202408040811", "田沼", 12, "Fourth")
        check_values("202408040811", "小林", 2, "Fourth")
        check_values("202408040811", "小林", 3, "First")
        check_values("202408040811", "小林", 4, "Star")
        check_values("202408040811", "小林", 5, "Third")
        check_values("202408040811", "小林", 7, "Second")
        check_values("202408040811", "小林", 10, "Fourth")
        check_values("202408040811", "小林", 12, "Fourth")
        check_values("202408040811", "藤村", 2, "Fourth")
        check_values("202408040811", "藤村", 4, "Fourth")
        check_values("202408040811", "藤村", 5, "Second")
        check_values("202408040811", "藤村", 7, "Star")
        check_values("202408040811", "藤村", 9, "Third")
        check_values("202408040811", "藤村", 12, "First")
        check_values("202408040811", "藤村", 13, "Fourth")
        check_values("202408040811", "大石川", 1, "Fourth")
        check_values("202408040811", "大石川", 2, "First")
        check_values("202408040811", "大石川", 3, "Second")
        check_values("202408040811", "大石川", 4, "Fourth")
        check_values("202408040811", "大石川", 7, "Third")
        check_values("202408040811", "大石川", 12, "Star")
        check_values("202408040811", "大石川", 13, "Fourth")
        check_values("202408040811", "CP予想", 1, "Third")
        check_values("202408040811", "CP予想", 2, "First")
        check_values("202408040811", "CP予想", 4, "Second")
        check_values("202408040811", "CP予想", 12, "Fourth")
        check_values("202408040811", "デスク", 2, "Fourth")
        check_values("202408040811", "デスク", 3, "Fourth")
        check_values("202408040811", "デスク", 4, "Fourth")
        check_values("202408040811", "デスク", 5, "Star")
        check_values("202408040811", "デスク", 7, "Second")
        check_values("202408040811", "デスク", 10, "Third")
        check_values("202408040811", "デスク", 12, "First")
        check_values("202408040811", "鈴木麻", 2, "First")
        check_values("202408040811", "鈴木正", 1, "Fourth")
        check_values("202408040811", "鈴木正", 2, "First")
        check_values("202408040811", "鈴木正", 3, "Star")
        check_values("202408040811", "鈴木正", 4, "Second")
        check_values("202408040811", "鈴木正", 7, "Third")
        check_values("202408040811", "鈴木正", 10, "Fourth")
        check_values("202408040811", "伊吹", 1, "Third")
        check_values("202408040811", "伊吹", 2, "Star")
        check_values("202408040811", "伊吹", 3, "Second")
        check_values("202408040811", "伊吹", 4, "Fourth")
        check_values("202408040811", "伊吹", 9, "Fourth")
        check_values("202408040811", "伊吹", 10, "First")