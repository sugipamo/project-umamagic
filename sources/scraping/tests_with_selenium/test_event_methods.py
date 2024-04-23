from django.test import TestCase
from scraping.models.webdriver import WebDriver
from scraping.models.login_for_scraping import LoginForScraping
from scraping.models.event_methods import Login, NetKeiba

class TestLoginMethods(TestCase):
    def test_update_logined(self):
        with WebDriver() as driver:
            login = LoginForScraping.objects.create(domain=".google.com", loggined=True)
            Login.update_logined(driver)
            login.refresh_from_db()
            self.assertEqual(login.loggined, False)

class TestNetKeiba(TestCase):
    def test_collect_raceids(self):
        NetKeiba.collect_raceids()
        with self.assertRaises(Exception):
            NetKeiba.collect_raceids()