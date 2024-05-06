from django.test import TestCase

from scraping.models.netkeiba_pages import PageCategory, Page
from scraping.models.netkeiba_pages import PageShutuba, PageResult, PageDbNetkeiba, PageYoso, PageYosoPro, PageYosoCp, PageOikiri

from scraping.model_utilitys.webdriver import WebDriver

class TestPageShutuba(TestCase):
    def test_html_update(self):
        category = PageCategory.objects.create(name="race.netkeiba.com")
        page = Page.objects.create(race_id="202408030606", category=category)
        page = PageShutuba(page_ptr=page)
        with WebDriver("eager") as driver:
            page.update_html(driver)

class TestPageResult(TestCase):
    def test_html_update(self):
        category = PageCategory.objects.create(name="race.netkeiba.com")
        page = Page.objects.create(race_id="202408030606", category=category)
        page = PageResult(page_ptr=page)
        with WebDriver("eager") as driver:
            page.update_html(driver)

class TestPageDbNetkeiba(TestCase):
    def test_html_update(self):
        category = PageCategory.objects.create(name="race.netkeiba.com")
        page = Page.objects.create(race_id="202408030606", category=category)
        page = PageDbNetkeiba(page_ptr=page)
        with WebDriver("eager") as driver:
            page.update_html(driver)

class TestPageYoso(TestCase):
    def test_html_update(self):
        category = PageCategory.objects.create(name="race.netkeiba.com")
        page = Page.objects.create(race_id="202408030606", category=category)
        page = PageYoso(page_ptr=page)
        with WebDriver("eager") as driver:
            page.update_html(driver)

class TestPageYosoPro(TestCase):
    def test_html_update(self):
        category = PageCategory.objects.create(name="race.netkeiba.com")
        page = Page.objects.create(race_id="202408030606", category=category)
        page = PageYosoPro(page_ptr=page)
        with WebDriver("eager") as driver:
            page.update_html(driver)

class TestPageYosoCp(TestCase):
    def test_html_update(self):
        category = PageCategory.objects.create(name="race.netkeiba.com")
        page = Page.objects.create(race_id="202408030606", category=category)
        page = PageYosoCp(page_ptr=page)
        with WebDriver("eager") as driver:
            page.update_html(driver)
        
class TestPageOikiri(TestCase):
    def test_html_update(self):
        category = PageCategory.objects.create(name="race.netkeiba.com")
        page = Page.objects.create(race_id="202408030606", category=category)
        page = PageOikiri(page_ptr=page)
        with WebDriver("eager") as driver:
            page.update_html(driver)