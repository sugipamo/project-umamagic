from django.test import TestCase
from scraping.models import ScrapeCategory, CrawlSchedule
from django.utils import timezone

class ScrapeCategoryModelTest(TestCase):
    def test_str(self):
        category = ScrapeCategory(name="テストカテゴリー")
        self.assertEqual(str(category), "テストカテゴリー")

class CrawlScheduleModelTest(TestCase):
    def test_str(self):
        category = ScrapeCategory(name="テストカテゴリー")
        schedule = CrawlSchedule(title="テストスケジュール", url="http://example.com", category=category)
        self.assertEqual(str(schedule), "テストスケジュール")

    def test_str_with_deleted_at(self):
        category = ScrapeCategory(name="テストカテゴリー")
        schedule = CrawlSchedule(title="テストスケジュール", url="http://example.com", category=category, deleted_at=timezone.now())
        self.assertEqual(str(schedule), "テストスケジュール")


