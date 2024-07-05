from django.db import models
from apps.web_controller.apps import TimeCounter, WebDriver
import gzip
import traceback
from functools import wraps
from urllib.error import URLError

NETKEIBA_BASE_URL = "https://www.netkeiba.com/"
NETKEIBA_DOMAIN = ".netkeiba.com"

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

    raceids = {}
    race_categorys = {}
    for url in urls:
        race_category = url.split("/")[2]
        if race_category not in {"nar.netkeiba.com", "race.netkeiba.com"}:
            continue
        category = race_categorys.get(race_category, PageCategory.objects.get_or_create(name=race_category)[0])
        params = url.split("?")[-1]
        params = dict([param.split("=") for param in params.split("&")])
        if "race_id" in params:
            race_id = params["race_id"]
            if race_id not in raceids:
                raceids[race_id] = Page.objects.get_or_create(race_id=race_id, category=category)[0]

class Page(models.Model):
    race_id = models.CharField(max_length=255)
    category = models.ForeignKey(PageCategory, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    url = NETKEIBA_BASE_URL
    need_login = False

    def __str__(self):
        return self.race_id

    def read_html(self):
        return gzip.decompress(self.html).decode()

    @classmethod
    @ensure_driver
    def extract_raceids(cls, driver):
        extract_raceids(driver)

    @ensure_driver
    def update_html(self, driver):
        if self.__class__ == Page:
            raise NotImplementedError("Pageクラスは直接使えません。")
        
        if not driver.current_url.startswith(self.url):
            driver.get(self.url)
        if "premium_new" in driver.current_url:
            self.loggined = False
            self.save()
            raise PermissionError("ログインが必要です。")
        self.html = gzip.compress(driver.page_source.encode())

        extract_raceids(driver)

    @classmethod
    def next(cls):
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
            page.save_base(raw=True)
        return page


class PageShutuba(Page):
    html = models.BinaryField(null=True, blank=True)
    @property
    def url(self):
        return f"https://{self.page_ptr.category.name}/race/shutuba.html?race_id={self.page_ptr.race_id}"

class PageResult(Page):
    html = models.BinaryField(null=True, blank=True)
    @property
    def url(self):
        return f"https://{self.page_ptr.category.name}/race/result.html?race_id={self.page_ptr.race_id}"
    
class PageDbNetkeiba(Page):
    html = models.BinaryField(null=True, blank=True)
    @property
    def url(self):
        return f"https://db.netkeiba.com/race/{self.page_ptr.race_id}"
    
class PageYoso(Page):
    html = models.BinaryField(null=True, blank=True)
    need_login = True
    @property
    def url(self):
        return f"https://{self.page_ptr.category.name}/yoso/mark_list.html?race_id={self.page_ptr.race_id}"



class PageYosoPro(Page):
    html = models.BinaryField(null=True, blank=True)
    need_login = True
    @property
    def url(self):
        return f"https://{self.page_ptr.category.name}/yoso/yoso_pro_opinion_list.html?race_id={self.page_ptr.race_id}"


class PageYosoCp(Page):
    html_rising = models.BinaryField(null=True, blank=True)
    html_precede = models.BinaryField(null=True, blank=True)
    html_spurt = models.BinaryField(null=True, blank=True)
    html_jockey = models.BinaryField(null=True, blank=True)
    html_trainer = models.BinaryField(null=True, blank=True)
    html_pedigree = models.BinaryField(null=True, blank=True)
    need_login = True
    @property
    def url(self):
        return f"https://{self.page_ptr.category.name}/yoso/yoso_cp.html?race_id={self.page_ptr.race_id}"
    
    def read_html(self):
        return [
            gzip.decompress(self.html_rising).decode(),
            gzip.decompress(self.html_precede).decode(),
            gzip.decompress(self.html_spurt).decode(),
            gzip.decompress(self.html_jockey).decode(),
            gzip.decompress(self.html_trainer).decode(),
            gzip.decompress(self.html_pedigree).decode(),
        ]

    @ensure_driver
    def update_html(self, driver):
        try:
            self.__update_html(driver)
        except Exception as e:
            with open("error.log", "a") as f:
                f.write(f"{str(e)}\n{traceback.format_exc()}")
        self.save_base(raw=True)

    def __update_html(self, driver):
        try:
            driver.get(self.url)
        except URLError as e:
            return
        
        if "premium_new" in driver.current_url:
            self.loggined = False
            self.save()
            raise PermissionError("ログインが必要です。")


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
        


class PageOikiri(Page):
    html = models.BinaryField(null=True, blank=True)
    need_login = True
    @property
    def url(self):
        if self.page_ptr.category.name == "nar.netkeiba.com":
            raise URLError("nar.netkeiba.comには追い切りページがありません。")
        return f"https://race.netkeiba.com/race/oikiri.html?race_id={self.page_ptr.race_id}&type=2"


# class PageOddsB1(Page):
#     html = models.BinaryField(null=True, blank=True)
#     @property
#     def url(self):
#         return f"https://{self.page_ptr.category.name}/odds/index.html?type=b1&race_id={self.page_ptr.race_id}"

# class PageOddsB3(Page):
#     html = models.BinaryField(null=True, blank=True)
#     @property
#     def url(self):
#         return f"https://{self.page_ptr.category.name}/odds/index.html?type=b3&race_id={self.page_ptr.race_id}"

# class PageOddsB4(Page):
#     html = models.BinaryField(null=True, blank=True)
#     @property
#     def url(self):
#         return f"https://{self.page_ptr.category.name}/odds/index.html?type=b4&race_id={self.page_ptr.race_id}"

# class PageOddsB5(Page):
#     html = models.BinaryField(null=True, blank=True)
#     @property
#     def url(self):
#         return f"https://{self.page_ptr.category.name}/odds/index.html?type=b5&race_id={self.page_ptr.race_id}"
    
# class PageOddsB6(Page):
#     html = models.BinaryField(null=True, blank=True)
#     @property
#     def url(self):
#         return f"https://{self.page_ptr.category.name}/odds/index.html?type=b6&race_id={self.page_ptr.race_id}"
    
# class PageOddsB7(Page):
#     html = models.BinaryField(null=True, blank=True)
#     @property
#     def url(self):
#         return f"https://{self.page_ptr.category.name}/odds/index.html?type=b7&race_id={self.page_ptr.race_id}"
    
# class PageOddsB8(Page):
#     html = models.BinaryField(null=True, blank=True)
#     @property
#     def url(self):
#         return f"https://{self.page_ptr.category.name}/odds/index.html?type=b8&race_id={self.page_ptr.race_id}"
    
# class PageOddsB9(Page):
#     html = models.BinaryField(null=True, blank=True)
#     @property
#     def url(self):
#         if self.page_ptr.category.name == "race.netkeiba.com":
#             raise URLError("race.netkeiba.comには枠単がありません。")
#         return f"https://{self.page_ptr.category.name}/odds/index.html?type=b9&race_id={self.page_ptr.race_id}"
    

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