from django.test import TestCase
from scraping.models.event_methods import Test


class TestEventMethods(TestCase):
    def test_default_methods(self):
        self.assertEqual(Test.default_methods(), None)

    def test_error_methods(self):
        with self.assertRaises(Exception):
            Test.error_methods()

    def test_access_google(self):
        with self.assertRaises(Exception):
            Test.access_google()

    def test_save_google_html(self):
        with self.assertRaises(Exception):
            Test.save_google_html()

