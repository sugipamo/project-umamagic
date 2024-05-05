from django.test import TestCase

from scraping.models.netkeiba_pages import RaceCategory, Race, Shutuba

class TestRaceCategory(TestCase):
    def test_str(self):
        category = RaceCategory.objects.create(name="example")
        self.assertEqual(str(category), "example")

    def test_get_or_create(self):
        category = RaceCategory.objects.get_or_create(name="example")[0]
        self.assertEqual(RaceCategory.objects.count(), 1)

class TestRace(TestCase):
    def setUp(self):
        category = RaceCategory.objects.create(name="example")
        self.race_id = Race.objects.create(race_id="00000000000", category=category)

    def test_str(self):
        self.assertEqual(str(self.race_id), "00000000000")

class TestShutuba(TestCase):
    def setUp(self):
        category = RaceCategory.objects.create(name="example")
        race = Race.objects.create(race_id="00000000000", category=category)
        self.shutuba = Shutuba(race_ptr=race)

    def test_str(self):
        self.assertEqual(str(self.shutuba.race_ptr.race_id), "00000000000")

    def test_save(self):
        self.shutuba.save_base(raw=True)