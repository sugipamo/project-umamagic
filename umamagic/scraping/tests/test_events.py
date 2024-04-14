from django.test import TestCase
from scraping.models.events import EventCategory, EventSchedule, EventArgs
from django.utils import timezone
from django.urls import reverse


class ScrapeCategoryModelTest(TestCase):
    def test_str(self):
        category = EventCategory(name="テストカテゴリー")
        self.assertEqual(str(category), "テストカテゴリー")

    def test_default_values(self):
        category = EventCategory(name="テストカテゴリー")
        self.assertEqual(category.use_method, "Test.default_methods")
        self.assertEqual(category.need_driver, False)

    def test_doevent_default_method(self):
        category = EventCategory(name="テストカテゴリー")
        self.assertEqual(category.doevent(), "テストカテゴリーのイベントを実行しました。")

    def test_doevent_error(self):
        category = EventCategory(name="エラー")
        category.use_method = "Test.error_methods"
        with self.assertRaises(Exception):
            category.doevent()


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


class EventScheduleListViewTest(TestCase):
    def test_event_schedule_list_view(self):
        response = self.client.get(reverse('scraping:event_schedule_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'scraping/event_schedule_list.html')
        self.assertContains(response, 'スケジュール')   
        self.assertQuerysetEqual(response.context['eventschedule_list'], [])

    def test_event_schedule_list_view_with_data(self):
        category = EventCategory.objects.create(name="テストカテゴリー")
        EventSchedule.objects.create(title="テストスケジュール", category=category)
        response = self.client.get(reverse('scraping:event_schedule_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'テストスケジュール')
        self.assertQuerysetEqual(response.context['eventschedule_list'], ['<EventSchedule: テストスケジュール>'])