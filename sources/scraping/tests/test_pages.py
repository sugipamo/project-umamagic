from django.test import TestCase

from scraping.models.pages import RaceIdCategory, RaceId, Shutuba

class TestRaceIdCategory(TestCase):
    def test_str(self):
        category = RaceIdCategory.objects.create(name="example")
        self.assertEqual(str(category), "example")

    def test_get_or_create(self):
        category = RaceIdCategory.objects.get_or_create(name="example")[0]
        self.assertEqual(RaceIdCategory.objects.count(), 1)

class TestRaceId(TestCase):
    def setUp(self):
        category = RaceIdCategory.objects.create(name="example")
        self.race_id = RaceId.objects.create(race_id="00000000000", category=category)

    def test_str(self):
        self.assertEqual(str(self.race_id), "00000000000")

class TestShutuba(TestCase):
    def setUp(self):
        category = RaceIdCategory.objects.create(name="example")
        race_id = RaceId.objects.create(race_id="00000000000", category=category)
        self.shutuba = Shutuba.objects.create(race_id=race_id)

    def test_str(self):
        self.assertEqual(str(self.shutuba.race_id), "00000000000")