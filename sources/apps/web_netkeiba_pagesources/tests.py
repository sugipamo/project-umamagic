from django.test import TestCase

from web_netkeiba_pagesources.models import Page
# Create your tests here.

class TestExtractRaceIds(TestCase):
    def test_extrace_raceids(self):
        Page.extract_raceids()
        self.assertTrue(Page.objects.all().count() > 0)