# 当サイトへのログインではなく、スクレイピングのためのログイン

from django.test import TestCase
from scraping.models import LoginForScraping
from django.urls import reverse

class LoginForScrapingModelTest(TestCase):
    def test_str(self):
        login_for_scraping = LoginForScraping.objects.create(domain='.example.com')
        self.assertEqual(str(login_for_scraping), '.example.com')

    def test_default_value(self):
        login_for_scraping = LoginForScraping.objects.create(domain='.example.com')
        self.assertEqual(login_for_scraping.loggined, False)

    def test_loggined(self):
        login_for_scraping = LoginForScraping.objects.create(domain='.example.com')
        login_for_scraping.loggined = True
        login_for_scraping.save()
        self.assertEqual(login_for_scraping.loggined, True)

class LoginForScrapingListViewTest(TestCase):
    def test_login_for_scraping_list_view(self):
        response = self.client.get(reverse('scraping:login_for_scraping_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'scraping/login_for_scraping_list.html')
        self.assertContains(response, 'ログイン待ち')

    def test_login_for_scraping_list_view_view_with_data(self):
        LoginForScraping.objects.create(domain='.example.com')
        response = self.client.get(reverse('scraping:login_for_scraping_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'scraping/login_for_scraping_list.html')
        self.assertContains(response, '.example.com')
