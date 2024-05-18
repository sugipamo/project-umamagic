from django.test import TestCase
from scraping.models.events import EventCategory, EventSchedule, EventArgs
from django.utils import timezone
from django.urls import reverse
from scraping.models.events import ScheduleError
from unittest import mock


class ScrapeCategoryModelTest(TestCase):
    def test_str(self):
        category = EventCategory(name="テストカテゴリー")
        self.assertEqual(str(category), "テストカテゴリー")

    def test_default_values(self):
        category = EventCategory(name="テストカテゴリー")
        self.assertEqual(category.use_method, "test.default_methods")
        self.assertEqual(category.need_driver, False)

    def test_doevent_default_method(self):
        category = EventCategory(name="テストカテゴリー")
        self.assertEqual(category.doevent(), True)

    def test_doevent_error(self):
        category = EventCategory(name="エラー")
        category.use_method = "test.error_methods"
        with self.assertRaises(Exception):
            category.doevent()


class EventArgsModelTest(TestCase):
    def test_str(self):
        eventargs = EventArgs(key="test_key", value="test_value")
        self.assertEqual(str(eventargs), "test_key: test_value")

    def test_setitem(self):
        schedule = EventSchedule(title="テストスケジュール", category=EventCategory(name="テストカテゴリー"))
        schedule.set_args("test_key", "test_value")
        self.assertEqual(schedule.get_args("test_key"), "test_value")

    def test_getitem(self):
        schedule = EventSchedule(title="テストスケジュール", category=EventCategory(name="テストカテゴリー"))
        schedule.set_args("test_key", "test_value")
        self.assertEqual(schedule.get_args("test_key"), "test_value")



class EventScheduleModelTest(TestCase):
    def test_str(self):
        schedule = EventSchedule(title="テストスケジュール", category=EventCategory(name="テストカテゴリー"))
        self.assertEqual(str(schedule), "テストスケジュール")

    def test_doevent_default_method(self):
        schedule = EventSchedule(title="テストスケジュール", category=EventCategory(name="テストカテゴリー"))
        self.assertEqual(schedule.doevent(), True)

    def test_doevent_error(self):
        category = EventCategory(name="エラー")
        schedule = EventSchedule.objects.create(title="エラー", category=category)
        schedule.status = 4
        with self.assertRaises(ScheduleError):
            schedule.doevent()

    def test_future_time_doevent(self):
        category = EventCategory(name="未来時間")
        schedule = EventSchedule.objects.create(title="未来時間", category=category)
        schedule.nextexecutedatetime = timezone.now() + timezone.timedelta(days=1)
        with self.assertRaises(ScheduleError):
            schedule.doevent()

    def test_done_doevent(self):
        category = EventCategory(name="過去時間")
        schedule = EventSchedule.objects.create(title="過去時間", category=category)
        schedule.status = 3
        schedule.nextexecutedatetime = timezone.now() - timezone.timedelta(days=1)
        with self.assertRaises(ScheduleError):
            schedule.doevent()

    @mock.patch("scraping.models.events.timezone.now")
    def test_parse_schedule_str(self, mock_now):
        category=EventCategory(name="テストカテゴリー", schedule_str="")
        schedule = EventSchedule(title="テストスケジュール", category=category)
        self.assertEqual(schedule.parse_schedule_str(""), (False, None, None))

        category=EventCategory(name="テストカテゴリー", schedule_str="0,1,2,")
        schedule = EventSchedule(title="テストスケジュール", category=category)
        mock_now.return_value = timezone.make_aware(timezone.datetime(2021, 1, 1, 0, 0, 0))
        self.assertEqual(schedule.parse_schedule_str("0"), (True, None, None))
        self.assertEqual(schedule.parse_schedule_str("0,"), (True, timezone.make_aware(timezone.datetime(2021, 1, 1, 0, 0, 0)), "0,1,2,"))
        self.assertEqual(schedule.parse_schedule_str("1,2,3,4,5"), (False, timezone.make_aware(timezone.datetime(2021, 1, 1, 0, 0, 1)), "0,2,3,4,5"))
        self.assertEqual(schedule.parse_schedule_str(""), (True, timezone.make_aware(timezone.datetime(2021, 1, 1, 0, 0, 1)), "0,2,"))
        
        mock_now.return_value = timezone.make_aware(timezone.datetime(2021, 7, 1, 0, 0, 0))
        self.assertEqual(schedule.parse_schedule_str("0"), (True, None, None))
        self.assertEqual(schedule.parse_schedule_str("0,"), (True, timezone.make_aware(timezone.datetime(2021, 7, 1, 0, 0, 0)), "0,1,2,"))
        self.assertEqual(schedule.parse_schedule_str("1,2,3,4,5"), (False, timezone.make_aware(timezone.datetime(2021, 7, 1, 0, 0, 1)), "0,2,3,4,5"))
        self.assertEqual(schedule.parse_schedule_str(""), (True, timezone.make_aware(timezone.datetime(2021, 7, 1, 0, 0, 1)), "0,2,"))

        mock_now.return_value = timezone.make_aware(timezone.datetime(2021, 7, 1, 12, 0, 0))
        self.assertEqual(schedule.parse_schedule_str("0"), (True, None, None))
        self.assertEqual(schedule.parse_schedule_str("0,"), (True, timezone.make_aware(timezone.datetime(2021, 7, 1, 12, 0, 0)), "0,1,2,"))
        self.assertEqual(schedule.parse_schedule_str("1,2,3,4,5"), (False, timezone.make_aware(timezone.datetime(2021, 7, 1, 12, 0, 1)), "0,2,3,4,5"))
        self.assertEqual(schedule.parse_schedule_str(""), (True, timezone.make_aware(timezone.datetime(2021, 7, 1, 12, 0, 1)), "0,2,"))


class EventScheduleListViewTest(TestCase):
    def test_event_schedule_list_view(self):
        response = self.client.get(reverse('scraping:event_schedule_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'scraping/event_schedule_list.html')
        self.assertContains(response, 'イベントスケジュール')

    def test_event_schedule_list_view_with_data(self):
        category = EventCategory.objects.create(name="テストカテゴリー")
        EventSchedule.objects.create(title="テストスケジュール", category=category)
        response = self.client.get(reverse('scraping:event_schedule_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'テストスケジュール')
        