from django.test import TestCase

from .models import PageCategory
from .models import Page
from .models import PageShutuba, PageResult, PageDbNetkeiba, PageYoso, PageYosoPro, PageYosoCp, PageOikiri

class MakeDummyDataTest(TestCase):
    def test_make_dummy_data(self):
        PageShutuba.make_dummy_instance()
        self.assertTrue(PageShutuba.objects.all().count() > 0)
        # self.assertTrue(PageResult.objects.all().count() > 0)
        # self.assertTrue(PageDbNetkeiba.objects.all().count() > 0)
        # self.assertTrue(PageYoso.objects.all().count() > 0)
        # self.assertTrue(PageYosoPro.objects.all().count() > 0)
        # self.assertTrue(PageYosoCp.objects.all().count() > 0)
        # self.assertTrue(PageOikiri.objects.all().count() > 0)

class NewPageTest(TestCase):
    def setUp(self):
        Page.extract_raceids()
        self.assertTrue(Page.objects.all().count() > 0)
        Page.objects.filter(category=PageCategory.objects.get_or_create(name="nar.netkeiba.com")[0]).delete()

    def test_PageShutuba(self):
        PageShutuba.new_page()
        self.assertTrue(PageShutuba.objects.all().count() > 0)

    def test_PageResult(self):
        PageResult.new_page()
        self.assertTrue(PageResult.objects.all().count() > 0)

    def test_PageDbNetkeiba(self):
        PageDbNetkeiba.new_page()
        self.assertTrue(PageDbNetkeiba.objects.all().count() > 0)

    def test_PageYoso(self):
        PageYoso.new_page()
        self.assertTrue(PageYoso.objects.all().count() > 0)

    def test_PageYosoPro(self):
        PageYosoPro.new_page()
        self.assertTrue(PageYosoPro.objects.all().count() > 0)

    def test_PageYosoCp(self):
        PageYosoCp.new_page()
        self.assertTrue(PageYosoCp.objects.all().count() > 0)

    def test_PageOikiri(self):
        PageOikiri.new_page()
        self.assertTrue(PageOikiri.objects.all().count() > 0)


