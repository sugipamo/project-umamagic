from django.test import TestCase
from scraping.models.events import EventCategory, EventSchedule, EventArgs


class EventScheduleModelTest(TestCase):
    def test_doevent_access_google(self):
        category = EventCategory(name="Googleアクセス")
        category.use_method = "Test.access_google"
        category.need_driver = True
        schedule = EventSchedule(title="Googleアクセス", category=category)
        schedule.set_args("url", "http://google.com")
        self.assertEqual(schedule.doevent(), "Googleアクセスのイベントを実行しました。")

    def test_doevent_access_google_error(self):
        category = EventCategory(name="Googleアクセス")
        category.use_method = "Test.access_google"
        category.need_driver = True
        schedule = EventSchedule(title="Googleアクセス", category=category)
        schedule.set_args("url", "")
        with self.assertRaises(Exception):
            schedule.doevent()

    def test_doevent_save_google_html(self):
        category = EventCategory(name="GoogleHtml取得")
        category.use_method = "Test.save_google_html"
        category.need_driver = True
        schedule = EventSchedule(title="GoogleHtml取得", category=category)
        schedule.set_args("url", "http://google.com")
        self.assertEqual(schedule.doevent(), "GoogleHtml取得のイベントを実行しました。")


# class EventScheduleModelLoginTest(TestCase):
#     def test_doevent_login_netkeiba(self):
#         category = EventCategory(name="Netkeibaログイン")
#         category.use_method = "LoginInfo.netkeiba"
#         category.need_driver = True
#         schedule = EventSchedule(title="Netkeibaログイン", category=category)
        # schedule.set_args("url", "https://regist.netkeiba.com/account/?pid=login")
#         schedule.set_args("username", "")
#         schedule.set_args("password", "")
#         self.assertEqual(schedule.doevent(), "Netkeibaログインのイベントを実行しました。")

    # def test_doevent_login_netkeiba_invalid_datas(self):
    #     category = EventCategory(name="Netkeibaログイン")
    #     category.use_method = "LoginInfo.netkeiba"
    #     category.need_driver = True
    #     schedule = EventSchedule(title="Netkeibaログイン", category=category)
    #     schedule.set_args("url", "https://regist.netkeiba.com/account/?pid=login")
#         schedule.set_args("username", "test")
#         schedule.set_args("password", "test")
    #     self.assertEqual(schedule.doevent(), "Netkeibaログインのイベントを実行できませんでした。")

