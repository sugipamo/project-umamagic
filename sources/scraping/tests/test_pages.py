from django.test import TestCase

from scraping.models.netkeiba_pages import PageCategory, Page
from scraping.models.netkeiba_pages import PageShutuba, PageResult, PageDbNetkeiba, PageYoso, PageYosoPro, PageYosoCp, PageOikiri

class TestPageCategory(TestCase):
    def test_str(self):
        category = PageCategory.objects.create(name="example")
        self.assertEqual(str(category), "example")

    def test_get_or_create(self):
        category = PageCategory.objects.get_or_create(name="example")[0]
        self.assertEqual(PageCategory.objects.count(), 1)

class TestPage(TestCase):
    def setUp(self):
        category = PageCategory.objects.create(name="example")
        self.race_id = Page.objects.create(race_id="00000000000", category=category)

    def test_str(self):
        self.assertEqual(str(self.race_id), "00000000000")

class TestPageShutuba(TestCase):
    def setUp(self):
        category = PageCategory.objects.create(name="example")
        race = Page.objects.create(race_id="00000000000", category=category)
        self.shutuba = PageShutuba(page_ptr=race)

    def test_str(self):
        self.assertEqual(str(self.shutuba.page_ptr.race_id), "00000000000")

    def test_save(self):
        self.shutuba.save_base(raw=True)

class TestPageResult(TestCase):
    def setUp(self):
        category = PageCategory.objects.create(name="example")
        race = Page.objects.create(race_id="00000000000", category=category)
        self.result = PageResult(page_ptr=race)

    def test_str(self):
        self.assertEqual(str(self.result.page_ptr.race_id), "00000000000")

    def test_save(self):
        self.result.save_base(raw=True)

class TestPageDbNetkeiba(TestCase):
    def setUp(self):
        category = PageCategory.objects.create(name="example")
        race = Page.objects.create(race_id="00000000000", category=category)
        self.dbnetkeiba = PageDbNetkeiba(page_ptr=race)

    def test_str(self):
        self.assertEqual(str(self.dbnetkeiba.page_ptr.race_id), "00000000000")

    def test_save(self):
        self.dbnetkeiba.save_base(raw=True)


class TestPageYoso(TestCase):
    def setUp(self):
        category = PageCategory.objects.create(name="example")
        race = Page.objects.create(race_id="00000000000", category=category)
        self.yoso = PageYoso(page_ptr=race)

    def test_str(self):
        self.assertEqual(str(self.yoso.page_ptr.race_id), "00000000000")

    def test_save(self):
        self.yoso.save_base(raw=True)

class TestPageYosoPro(TestCase):
    def setUp(self):
        category = PageCategory.objects.create(name="example")
        race = Page.objects.create(race_id="00000000000", category=category)
        self.yosopro = PageYosoPro(page_ptr=race)

    def test_str(self):
        self.assertEqual(str(self.yosopro.page_ptr.race_id), "00000000000")

    def test_save(self):
        self.yosopro.save_base(raw=True)

class TestPageYosoCp(TestCase):
    def setUp(self):
        category = PageCategory.objects.create(name="example")
        race = Page.objects.create(race_id="00000000000", category=category)
        self.yosocp = PageYosoCp(page_ptr=race)

    def test_str(self):
        self.assertEqual(str(self.yosocp.page_ptr.race_id), "00000000000")

    def test_save(self):
        self.yosocp.save_base(raw=True)
        
class TestPageOikiri(TestCase):
    def setUp(self):
        category = PageCategory.objects.create(name="example")
        race = Page.objects.create(race_id="00000000000", category=category)
        self.oikiri = PageOikiri(page_ptr=race)

    def test_str(self):
        self.assertEqual(str(self.oikiri.page_ptr.race_id), "00000000000")

    def test_save(self):
        self.oikiri.save_base(raw=True)