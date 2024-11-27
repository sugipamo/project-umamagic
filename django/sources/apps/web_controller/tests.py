from django.test import TestCase

class TestWebDriver(TestCase):
    def test_webdriver(self):
        from .apps import WebDriver
        with WebDriver(url="https://www.google.com/") as driver:
            pass
        self.assertTrue(True)