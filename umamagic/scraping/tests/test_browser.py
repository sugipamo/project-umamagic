from django.test import TestCase
from scraping.models import EventCategory, EventSchedule, EventArgs


class EventScheduleModelTest(TestCase):
    def test_doevent_access_google(self):
        category = EventCategory(name="Googleアクセス")
        category.use_method = "test.access_google"
        category.need_driver = True
        schedule = EventSchedule(title="Googleアクセス", category=category)
        schedule["url"] = "http://google.com"
        self.assertEqual(schedule.doevent(), "Googleアクセスのイベントを実行しました。")

    def test_doevent_access_google_error(self):
        category = EventCategory(name="Googleアクセス")
        category.use_method = "test.access_google"
        category.need_driver = True
        schedule = EventSchedule(title="Googleアクセス", category=category)
        schedule["url"] = ""
        self.assertEqual(schedule.doevent(), "Googleアクセスのイベントを実行できませんでした。")

    def test_doevent_save_google_html(self):
        category = EventCategory(name="GoogleHtml取得")
        category.use_method = "test.save_google_html"
        category.need_driver = True
        schedule = EventSchedule(title="GoogleHtml取得", category=category)
        schedule["url"] = "http://google.com"
        schedule["htmlpath"] = "test/google.html"
        self.assertEqual(schedule.doevent(), "GoogleHtml取得のイベントを実行しました。")

