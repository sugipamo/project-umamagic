from django.test import TestCase
from scraping.models import ScrapeCategory, EventSchedule, EventArgs
from django.utils import timezone

class ScrapeCategoryModelTest(TestCase):
    def test_str(self):
        category = ScrapeCategory(name="テストカテゴリー")
        self.assertEqual(str(category), "テストカテゴリー")

class EventScheduleModelTest(TestCase):
    def setUp(self):
        pass

    def test_str(self):
        schedule = EventSchedule(title="テストスケジュール", category=ScrapeCategory(name="テストカテゴリー"))
        self.assertEqual(str(schedule), "テストスケジュール")

    def test_doevent_default_method(self):
        schedule = EventSchedule(title="テストスケジュール", category=ScrapeCategory(name="テストカテゴリー"))
        self.assertEqual(schedule.doevent(), "テストカテゴリーのイベントを実行しました。")

    def test_doevent_access_google(self):
        category = ScrapeCategory(name="Googleアクセス")
        category.use_method = "access_google"
        category.need_driver = True
        schedule = EventSchedule(title="Googleアクセス", category=category)
        schedule["url"] = "http://google.com"
        self.assertEqual(schedule.doevent(), "Googleアクセスのイベントを実行しました。")