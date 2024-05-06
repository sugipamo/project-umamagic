from django.test import TestCase
from scraping.model_utilitys.webdriver import WebDriver
from scraping.models.login_for_scraping import LoginForScraping
from scraping.model_utilitys.event_methods import login_for_scraping, netkeiba
from scraping.models.netkeiba_pages import Page

class TestLoginMethods(TestCase):
    def test_update_logined(self):
        login = LoginForScraping.objects.create(domain=".google.com", loggined=True)
        with WebDriver() as driver:
            login.update_logined(driver)
        login.refresh_from_db()
        self.assertEqual(login.loggined, False)

class TestNetKeiba(TestCase):
    def setUp(self):
        login = LoginForScraping.objects.create(domain=".netkeiba.com", loggined=True)
        with WebDriver() as driver:
            login.update_logined(driver)

        self.assertFalse(Page.objects.exists())
        with WebDriver() as driver:
            netkeiba.new_raceids(driver)
        self.assertTrue(Page.objects.exists())

    def test_update_logined(self):
        self.assertEqual(LoginForScraping.objects.get(domain=".netkeiba.com").loggined, True)
        
    def test_new_page(self):
        with WebDriver() as driver:
            race = netkeiba.new_page(driver)
        self.assertTrue(race)