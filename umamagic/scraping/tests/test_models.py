from django.test import TestCase
from scraping.models import EventCategory, EventSchedule, EventArgs
from unittest import mock
from datetime import datetime
from django.utils import timezone

class ScrapeCategoryModelTest(TestCase):
    def test_str(self):
        category = EventCategory(name="テストカテゴリー")
        self.assertEqual(str(category), "テストカテゴリー")

    def test_default_values(self):
        category = EventCategory(name="テストカテゴリー")
        self.assertEqual(category.use_method, "default_methods")
        self.assertEqual(category.need_driver, False)

    def test_doevent_default_method(self):
        category = EventCategory(name="テストカテゴリー")
        self.assertEqual(category.doevent(), "テストカテゴリーのイベントを実行しました。")



class EventArgsModelTest(TestCase):
    def test_str(self):
        eventargs = EventArgs(key="test_key", value="test_value")
        self.assertEqual(str(eventargs), "test_key: test_value")

    def test_setitem(self):
        schedule = EventSchedule(title="テストスケジュール", category=EventCategory(name="テストカテゴリー"))
        schedule["test_key"] = "test_value"
        self.assertEqual(schedule["test_key"], "test_value")

    def test_getitem(self):
        schedule = EventSchedule(title="テストスケジュール", category=EventCategory(name="テストカテゴリー"))
        schedule["test_key"] = "test_value"
        self.assertEqual(schedule["test_key"], "test_value")


class EventScheduleModelTest(TestCase):
    def test_str(self):
        schedule = EventSchedule(title="テストスケジュール", category=EventCategory(name="テストカテゴリー"))
        self.assertEqual(str(schedule), "テストスケジュール")

    def test_doevent_default_method(self):
        schedule = EventSchedule(title="テストスケジュール", category=EventCategory(name="テストカテゴリー"))
        self.assertEqual(schedule.doevent(), "テストカテゴリーのイベントを実行しました。")

    def test_doevent_error(self):
        category = EventCategory(name="エラー")
        schedule = EventSchedule.objects.create(title="エラー", category=category)
        schedule.status = 4
        self.assertEqual(schedule.doevent(), "エラーはエラーが発生しています。")

    def test_future_time_doevent(self):
        category = EventCategory(name="未来時間")
        schedule = EventSchedule.objects.create(title="未来時間", category=category)
        schedule.startdatetime = timezone.now() + timezone.timedelta(days=1)
        self.assertEqual(schedule.doevent(), "未来時間はまだ実行できません。")

    def test_past_time_doevent(self):
        category = EventCategory(name="過去時間")
        schedule = EventSchedule.objects.create(title="過去時間", category=category)
        schedule.enddatetime = timezone.now() - timezone.timedelta(days=1)
        self.assertEqual(schedule.doevent(), "過去時間は既に終了しています。")