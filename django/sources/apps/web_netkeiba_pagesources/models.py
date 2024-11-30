from django.db import models
from apps.web_controller.models import LoginForScraping, WebDriver, TimeCounter
from django.utils import timezone
import gzip
import traceback
import pickle
from pathlib import Path
from functools import wraps
from urllib.error import URLError

NETKEIBA_BASE_URL = "https://www.netkeiba.com/"
NETKEIBA_DOMAIN = ".netkeiba.com"

class BasePageSourceParser(models.Model):
    success_parsing = models.BooleanField(default=False, verbose_name='パース成功フラグ')
    need_update_at = models.DateTimeField(null=True, verbose_name='次回更新日時')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')

    class Meta:
        abstract = True

    def __str__(self):
        return self.page_source.race_id

    @classmethod
    def next(cls, relate_model):
        parser = None
        unused_sources = relate_model.objects.exclude(page_ptr_id__in=cls.objects.values_list('page_source_id', flat=True))
        unused_source = unused_sources.filter(need_update=False).order_by("created_at").last()
        if unused_source is not None:
            parser = cls(
                page_source = unused_source,
                need_update_at = timezone.now() + timezone.timedelta(days=1)
            )
            parser.save()

        unupdated_parsers = cls.objects.filter(need_update_at__lte=timezone.now())
        for unupdated_parser in unupdated_parsers:
            unupdated_parser.page_source.need_update = True
            unupdated_parser.page_source.save()
            unupdated_parser.delete()

        return parser

class PageCategory(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

def ensure_driver(method):
    @wraps(method)
    def wrapper(self_or_cls, *args, **kwargs):
        try:
            new_kwargs = {"url": self_or_cls.url}
        except URLError as e:
            return
        for arg in args:
            if type(arg) == WebDriver:
                new_kwargs['driver'] = arg
                break

        if 'driver' not in kwargs or kwargs['driver'] is None:
            if self_or_cls.need_login:
                new_kwargs["domain"] = NETKEIBA_DOMAIN
            with WebDriver(**new_kwargs) as driver:
                kwargs['driver'] = driver
                return method(self_or_cls, *args, **kwargs)
        else:
            return method(self_or_cls, *args, **kwargs)
    return wrapper
    
def extract_raceids(driver):
    with TimeCounter() as tc:
        elems = tc.do(driver.find_elements, "xpath", ".//a")
    elems = driver.find_elements("xpath", ".//a[contains(@href, 'race_id')]")
    urls = {elem.get_attribute("href") for elem in elems}

    raceids = set()
    for url in urls:
        domain_name = url.split("/")[2]
        if domain_name not in {"nar.netkeiba.com", "race.netkeiba.com"}:
            continue
        race_category = domain_name.split(".")[0]
        category, _ = PageCategory.objects.get_or_create(name=race_category)
        params = url.split("?")[-1]
        params = dict([param.split("=") for param in params.split("&")])
        if "race_id" in params:
            race_id = params["race_id"].replace(" ", "")
            if race_id == "":
                continue
            raceids.add(race_id)

    unregisted_raceids = raceids - set(Page.objects.values_list())
    for race_id in unregisted_raceids:
        page = Page(race_id=race_id, category=category)
        page.save()


class Page(models.Model):
    race_id = models.CharField(max_length=255)
    category = models.ForeignKey(PageCategory, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    url = NETKEIBA_BASE_URL
    need_login = False

    @classmethod
    @ensure_driver
    def extract_raceids(cls, driver):
        extract_raceids(driver)

    def __str__(self):
        return f"{self.race_id} - {self.category.name}"

class BasePage(models.Model):
    need_update = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    need_login = False

    class Meta:
        abstract = True

    def __str__(self):
        return self.race_id
    
    @property
    def race_id(self):
        return self.page_ptr.race_id

    def read_html(self):
        if self.html is None:
            return None
        return gzip.decompress(self.html).decode()

    @ensure_driver
    def update_html(self, driver):
        if self.__class__ == Page:
            raise NotImplementedError("Pageクラスは直接使えません。")
        
        if not driver.current_url.startswith(self.url):
            driver.get(self.url)
        elif self.need_login:
            driver.get(self.url)

        if "premium_new" in driver.current_url:
            login, _ = LoginForScraping.objects.get_or_create(domain=NETKEIBA_DOMAIN)
            login.loggined = False
            login.save()
            return
        
        self.extract_html_from_driver(driver=driver)
        self.need_update = False
        self.save_base(raw=True)
        
        extract_raceids(driver)

    def extract_html_from_driver(self, driver):
        self.html = gzip.compress(driver.page_source.encode())

    @classmethod
    def next(cls):
        need_update_races = cls.objects.filter(need_update=True)
        if need_update_races:
            need_update_race = need_update_races.first()
            return need_update_race

        unused_races = Page.objects.exclude(race_id__in=cls.objects.values_list('race_id', flat=True))
        unused_race = unused_races.order_by("created_at").first()
        if unused_race:
            race = cls(page_ptr=unused_race)
            return race
        return None
    
    @classmethod
    def new_page(cls):
        page = cls.next()
        if page:
            page.update_html()
        return page
    
    @property
    def html_pickle_for_dummy_path(self):
        path = Path(__file__).parent / "html_pickles" / f"{self.__class__.__name__}_{self.page_ptr.race_id}.pickle"
        path.parent.mkdir(exist_ok=True)
        return path

    def make_pickle_for_dummy(self):
        with open(self.html_pickle_for_dummy_path, "wb") as f:
            pickle.dump(self, f)

    def read_pickle_for_dummy(self):
        path = self.html_pickle_for_dummy_path
        if not path.exists():
            return 
        with open(path, "rb") as f:
            data = pickle.load(f)
        self.html = data.html
    
    @classmethod
    def make_dummy_instance(cls, category=None, race_id=None):
        from random import choice, randint
        category_name = category or choice(["nar", "race"])
        page = Page(
            race_id = (race_id or str(randint(1000000, 9999999))), 
            category=PageCategory.objects.get_or_create(name=category_name)[0]
        )
        page.save()
        page_instance = cls(page_ptr=page)
        if category or race_id:
            path = page_instance.html_pickle_for_dummy_path
            if path.exists():
                page_instance.read_pickle_for_dummy()
            else:
                page_instance.update_html()
                page_instance.make_pickle_for_dummy()
        page_instance.save_base(raw=True)
        return page_instance
    
    def break_down(self):
        self.delete()

class PageShutuba(Page, BasePage):
    html = models.BinaryField(null=True, blank=True)
    @property
    def url(self):
        return f"https://{self.page_ptr.category.name}.netkeiba.com/race/shutuba.html?race_id={self.page_ptr.race_id}"

class PageResult(Page, BasePage):
    html = models.BinaryField(null=True, blank=True)
    @property
    def url(self):
        return f"https://{self.page_ptr.category.name}.netkeiba.com/race/result.html?race_id={self.page_ptr.race_id}"
    
class PageDbNetkeiba(Page, BasePage):
    html = models.BinaryField(null=True, blank=True)
    @property
    def url(self):
        return f"https://db.netkeiba.com/race/{self.page_ptr.race_id}"
    
class PageYoso(Page, BasePage):
    html = models.BinaryField(null=True, blank=True)
    need_login = True
    @property
    def url(self):
        return f"https://{self.page_ptr.category.name}.netkeiba.com/yoso/mark_list.html?race_id={self.page_ptr.race_id}"

class PageYosoPro(Page, BasePage):
    html = models.BinaryField(null=True, blank=True)
    need_login = True
    @property
    def url(self):
        return f"https://{self.page_ptr.category.name}.netkeiba.com/yoso/yoso_pro_opinion_list.html?race_id={self.page_ptr.race_id}"


class PageYosoCp(Page, BasePage):
    html_rising = models.BinaryField(null=True, blank=True)
    html_precede = models.BinaryField(null=True, blank=True)
    html_spurt = models.BinaryField(null=True, blank=True)
    html_jockey = models.BinaryField(null=True, blank=True)
    html_trainer = models.BinaryField(null=True, blank=True)
    html_pedigree = models.BinaryField(null=True, blank=True)
    need_login = True
    @property
    def url(self):
        return f"https://{self.page_ptr.category.name}.netkeiba.com/yoso/yoso_cp.html?race_id={self.page_ptr.race_id}"
    
    def read_html(self):
        return {
            "rising": gzip.decompress(self.html_rising).decode(),
            "precede": gzip.decompress(self.html_precede).decode(),
            "spurt": gzip.decompress(self.html_spurt).decode(),
            "jockey": gzip.decompress(self.html_jockey).decode(),
            "trainer": gzip.decompress(self.html_trainer).decode(),
            "pedigree": gzip.decompress(self.html_pedigree).decode(),
        }

    @ensure_driver
    def extract_html_from_driver(self, driver):
        try:
            self.__extract_html_from_driver(driver)
        except Exception as e:
            pass
            # with open("error.log", "a") as f:
            #     f.write(f"{str(e)}\n{traceback.format_exc()}")

    def __extract_html_from_driver(self, driver):
        htmls = [self.html_rising, self.html_precede, self.html_spurt, self.html_jockey, self.html_trainer, self.html_pedigree]
        for i in range(len(htmls)):
            with TimeCounter() as tc:
                trs = tc.do(driver.find_elements, "xpath", ".//table[@class='CP_Setting']/tbody/tr")
            
            for tr in trs:
                tr.find_elements("xpath", ".//td/label")[0].click()
            trs[i].find_elements("xpath", ".//td/label")[-1].click()
            driver.find_elements("xpath", ".//input[@value='設定']")[0].click()
            with TimeCounter() as tc:
                tc.do(driver.find_elements, "xpath", ".//table[@class='Yoso01_Table Default']")
            
            htmls[i] = gzip.compress(driver.page_source.encode())
        
        self.html_rising, self.html_precede, self.html_spurt, self.html_jockey, self.html_trainer, self.html_pedigree = htmls
        
    def read_pickle_for_dummy(self):
        path = self.html_pickle_for_dummy_path
        if not path.exists():
            return 
        with open(path, "rb") as f:
            data = pickle.load(f)
        self.html_rising = data.html_rising
        self.html_precede = data.html_precede
        self.html_spurt = data.html_spurt
        self.html_jockey = data.html_jockey
        self.html_trainer = data.html_trainer
        self.html_pedigree = data.html_pedigree

class PageOikiri(Page, BasePage):
    html = models.BinaryField(null=True, blank=True)
    need_login = True
    @property
    def url(self):
        if self.page_ptr.category.name == "nar.netkeiba.com":
            raise URLError("nar.netkeiba.comには追い切りページがありません。")
        return f"https://race.netkeiba.com/race/oikiri.html?race_id={self.page_ptr.race_id}&type=2"


# class PageOddsB1(Page, BasePage):
#     html = models.BinaryField(null=True, blank=True)
#     @property
#     def url(self):
#         return f"https://{self.page_ptr.category.name}.netkeiba.com/odds/index.html?type=b1&race_id={self.page_ptr.race_id}"

# class PageOddsB3(Page, BasePage):
#     html = models.BinaryField(null=True, blank=True)
#     @property
#     def url(self):
#         return f"https://{self.page_ptr.category.name}.netkeiba.com/odds/index.html?type=b3&race_id={self.page_ptr.race_id}"

# class PageOddsB4(Page, BasePage):
#     html = models.BinaryField(null=True, blank=True)
#     @property
#     def url(self):
#         return f"https://{self.page_ptr.category.name}.netkeiba.com/odds/index.html?type=b4&race_id={self.page_ptr.race_id}"

# class PageOddsB5(Page, BasePage):
#     html = models.BinaryField(null=True, blank=True)
#     @property
#     def url(self):
#         return f"https://{self.page_ptr.category.name}.netkeiba.com/odds/index.html?type=b5&race_id={self.page_ptr.race_id}"
    
# class PageOddsB6(Page, BasePage):
#     html = models.BinaryField(null=True, blank=True)
#     @property
#     def url(self):
#         return f"https://{self.page_ptr.category.name}.netkeiba.com/odds/index.html?type=b6&race_id={self.page_ptr.race_id}"
    
# class PageOddsB7(Page, BasePage):
#     html = models.BinaryField(null=True, blank=True)
#     @property
#     def url(self):
#         return f"https://{self.page_ptr.category.name}.netkeiba.com/odds/index.html?type=b7&race_id={self.page_ptr.race_id}"
    
# class PageOddsB8(Page, BasePage):
#     html = models.BinaryField(null=True, blank=True)
#     @property
#     def url(self):
#         return f"https://{self.page_ptr.category.name}.netkeiba.com/odds/index.html?type=b8&race_id={self.page_ptr.race_id}"
    
# class PageOddsB9(Page, BasePage):
#     html = models.BinaryField(null=True, blank=True)
#     @property
#     def url(self):
#         if self.page_ptr.category.name == "race.netkeiba.com":
#             raise URLError("race.netkeiba.comには枠単がありません。")
#         return f"https://{self.page_ptr.category.name}.netkeiba.com/odds/index.html?type=b9&race_id={self.page_ptr.race_id}"
    

class Pages():
    PageClasses = [
        PageShutuba,
        PageResult,
        PageDbNetkeiba,
        PageYoso,
        PageYosoPro,
        PageYosoCp,
        PageOikiri,
        # PageOddsB1,
        # PageOddsB3,
        # PageOddsB4,
        # PageOddsB5,
        # PageOddsB6,
        # PageOddsB7,
        # PageOddsB8,
        # PageOddsB9,
    ]