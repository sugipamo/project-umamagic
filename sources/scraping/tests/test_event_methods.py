from django.test import TestCase
from scraping.utilitys.event_methods import test


class TestEventMethods(TestCase):
    def test_default_methods(self):
        self.assertEqual(test.default_methods(), None)

    def test_error_methods(self):
        with self.assertRaises(Exception):
            test.error_methods()

    def test_access_google(self):
        with self.assertRaises(Exception):
            test.access_google()

    def test_save_google_html(self):
        with self.assertRaises(Exception):
            test.save_google_html()

