from django.test import TestCase
from scraping.model_utilitys.webdriver import WebDriver
from scraping.models.login_for_scraping import LoginForScraping
from scraping.model_utilitys.event_methods import login_for_scraping, netkeiba
from scraping.models.pages import Race, Shutuba

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

    def test_update_logined(self):
        self.assertEqual(LoginForScraping.objects.get(domain=".netkeiba.com").loggined, True)

    def test_extract_raceids(self):
        self.assertFalse(Race.objects.exists())
        with WebDriver() as driver:
            driver.get("https://www.netkeiba.com/")
            netkeiba.extract_raceids(driver)
        self.assertTrue(Race.objects.exists())

    def test_new_raceids(self):
        self.assertFalse(Race.objects.exists())
        with WebDriver() as driver:
            netkeiba.new_raceids(driver)
        self.assertTrue(Race.objects.exists())
        

    def test_new_shutuba(self):
        self.assertFalse(Race.objects.exists())
        self.assertFalse(Shutuba.objects.exists())
        with WebDriver() as driver:
            netkeiba.new_raceids(driver)
            netkeiba.new_shutuba(driver)
        self.assertTrue(Race.objects.exists())
        self.assertTrue(Shutuba.objects.exists())