from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from .models import Schedule, ScheduleDoeventHistory, doevent



class AutoExecutionTests(TestCase):
    def test_doevent(self):
        response = doevent()
        self.assertIn("doevent datetime:", response)

class AutoExecutionTests(TestCase):
    def test_schedule_deletion(self):
        Schedule.objects.create(
            status=1,
            event_function="test_event",
            nextexecutedatetime=timezone.now()
        )

        doevent()

        with self.assertRaises(Schedule.DoesNotExist):
            Schedule.objects.get(event_function="test_event")

class ScheduleModelTests(TestCase):
    
    def setUp(self):
        self.schedule = Schedule.objects.create(
            status=1,
            event_function="test_event",
            nextexecutedatetime=timezone.now()
        )

    def test_schedule_creation(self):
        self.assertEqual(self.schedule.status, 1)
        self.assertEqual(self.schedule.event_function, "test_event")

    def test_doevent(self):
        response = self.schedule.doevent()
        self.assertIn("doevent datetime:", response)
    
    def test_event_schedule_doevent_history_creation(self):
        history = ScheduleDoeventHistory(
            schedule=self.schedule,
            event_function="test_event"
        )
        self.assertEqual(history.schedule, self.schedule)
        self.assertEqual(history.event_function, "test_event")



class ScheduleViewsTests(TestCase):

    def setUp(self):
        self.schedule = Schedule.objects.create(
            status=1,
            event_function="test_event",
            nextexecutedatetime=timezone.now()
        )

    def test_event_schedule_list_view(self):
        response = self.client.get(reverse('event_schedules:event_schedule_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "test_event")

    def test_event_schedule_doevent_view(self):
        response = self.client.get(reverse('event_schedules:doevent'))
        self.assertEqual(response.status_code, 200)
        self.assertIn("doevent datetime:", str(response.content))

    def test_event_schedule_solve_error_view(self):
        self.schedule.status = 4
        self.schedule.save()
        response = self.client.get(reverse('event_schedules:event_schedule_solve_error', args=[self.schedule.pk]))
        self.assertEqual(response.status_code, 302)  # Redirect status code
        self.schedule.refresh_from_db()
        self.assertEqual(self.schedule.status, 1)

class URLTests(TestCase):

    def test_event_schedule_list_url(self):
        response = self.client.get(reverse('event_schedules:event_schedule_list'))
        self.assertEqual(response.status_code, 200)

    def test_event_schedule_doevent_url(self):
        response = self.client.get(reverse('event_schedules:doevent'))
        self.assertEqual(response.status_code, 200)