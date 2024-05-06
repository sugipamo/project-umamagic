from django.test import TestCase
from scraping.models.events import EventCategory, EventSchedule, EventArgs


class EventScheduleBrowserTest(TestCase):
    def test_doevent_access_google(self):
        category = EventCategory(name="Googleアクセス")
        category.use_method = "test.access_google"
        category.need_driver = True
        schedule = EventSchedule(title="Googleアクセス", category=category)
        schedule.set_args("url", "http://google.com")
        self.assertEqual(schedule.doevent(), True)

    def test_doevent_access_google_error(self):
        category = EventCategory(name="Googleアクセス")
        category.use_method = "test.access_google"
        category.need_driver = True
        schedule = EventSchedule(title="Googleアクセス", category=category)
        schedule.set_args("url", "")
        with self.assertRaises(Exception):
            schedule.doevent()

    def test_doevent_save_google_html(self):
        category = EventCategory(name="GoogleHtml取得")
        category.use_method = "test.save_google_html"
        category.need_driver = True
        schedule = EventSchedule(title="GoogleHtml取得", category=category)
        schedule.set_args("url", "http://google.com")
        self.assertEqual(schedule.doevent(), True)
