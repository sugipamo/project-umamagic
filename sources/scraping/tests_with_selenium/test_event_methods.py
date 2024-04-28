from django.test import TestCase
from scraping.model_utilitys.webdriver import WebDriver
from scraping.models.login_for_scraping import LoginForScraping
from scraping.model_utilitys.event_methods import login_for_scraping, netkeiba

class TestLoginMethods(TestCase):
    def test_update_logined(self):
        login = LoginForScraping.objects.create(domain=".google.com", loggined=True)
        with WebDriver() as driver:
            login.update_logined(driver)
        login.refresh_from_db()
        self.assertEqual(login.loggined, False)

class TestNetKeiba(TestCase):
    def setup_method(self):
        login = LoginForScraping.objects.create(domain=".netkeiba.com", loggined=True)
        with WebDriver() as driver:
            login.update_logined(driver)
        login.refresh_from_db()
        self.assertEqual(login.loggined, True)

    def test_extract_raceids(self):
        LoginForScraping.objects.create(domain=".netkeiba.com", loggined=True)
        with WebDriver() as driver:
            ret = netkeiba.extract_raceids(driver, "https://www.netkeiba.com/")
        self.assertTrue(ret)

    def test_new_raceids(self):
        LoginForScraping.objects.create(domain=".netkeiba.com", loggined=True)
        with WebDriver() as driver:
            netkeiba.new_raceids(driver)