from django.db import models
from django.db.models import Q
from scraping.models.login_for_scraping import cookie_required
from scraping.models.login_for_scraping import LoginForScraping
from scraping.model_utilitys.webdriver import TimeCounter
import gzip
import traceback

class NonUrlError(Exception):
    pass

class PageCategory(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Page(models.Model):
    race_id = models.CharField(max_length=255)
    category = models.ForeignKey(PageCategory, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def need_cookie(cls):
        return False

    def __str__(self):
        return self.race_id

    def read_html(self):
        return gzip.decompress(self.html).decode()

    def update_html(self, driver):
        if self.__class__ == Page:
            raise NotImplementedError("Pageクラスは直接使えません。")
        
        if not self.page_ptr.category.name in {"nar.netkeiba.com", "race.netkeiba.com"}:
            return
        try:
            driver.get(self.url)
        except NonUrlError as e:
            return
        
        if self.need_cookie() and "premium_new" in driver.current_url:
            domain = LoginForScraping.objects.get(domain=".netkeiba.com")
            domain.loggined = False
            domain.save()
            raise NonUrlError("ログインが必要です。")

        self.html = gzip.compress(driver.page_source.encode())

    @classmethod
    def next_raceid(cls):
        unused_races = Page.objects.exclude(race_id__in=cls.objects.values_list('race_id', flat=True))
        unused_races = unused_races.filter(
            Q(category__name="nar.netkeiba.com") |
            Q(category__name="race.netkeiba.com")
        )
        unused_race = unused_races.order_by("created_at").first()
        if unused_race:
            shutuba = cls(page_ptr=unused_race)
            return shutuba

        return None



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
    @property
    def url(self):
        return f"https://{self.page_ptr.category.name}/yoso/mark_list.html?race_id={self.page_ptr.race_id}"

    @classmethod
    def need_cookie(cls):
        return True

    @cookie_required(".netkeiba.com")
    def update_html(self, driver):
        super().update_html(driver)

class PageYosoPro(Page):
    html = models.BinaryField(null=True, blank=True)
    @property
    def url(self):
        return f"https://{self.page_ptr.category.name}/yoso/yoso_pro_opinion_list.html?race_id={self.page_ptr.race_id}"

    @classmethod
    def need_cookie(cls):
        return True
    
    @cookie_required(".netkeiba.com")
    def update_html(self, driver):
        super().update_html(driver)

class PageYosoCp(Page):
    html_rising = models.BinaryField(null=True, blank=True)
    html_precede = models.BinaryField(null=True, blank=True)
    html_spurt = models.BinaryField(null=True, blank=True)
    html_jockey = models.BinaryField(null=True, blank=True)
    html_trainer = models.BinaryField(null=True, blank=True)
    html_pedigree = models.BinaryField(null=True, blank=True)

    @property
    def url(self):
        return f"https://{self.page_ptr.category.name}/yoso/yoso_cp.html?race_id={self.page_ptr.race_id}"

    @classmethod
    def need_cookie(cls):
        return True
    
    def read_html(self):
        return [
            gzip.decompress(self.html_rising).decode(),
            gzip.decompress(self.html_precede).decode(),
            gzip.decompress(self.html_spurt).decode(),
            gzip.decompress(self.html_jockey).decode(),
            gzip.decompress(self.html_trainer).decode(),
            gzip.decompress(self.html_pedigree).decode(),
        ]


    def update_html(self, driver):
        try:
            self.__update_html(driver)
        except Exception as e:
            with open("error.log", "a") as f:
                f.write(f"{str(e)}\n{traceback.format_exc()}")

    @cookie_required(".netkeiba.com")
    def __update_html(self, driver):
        if not self.page_ptr.category.name in {"nar.netkeiba.com", "race.netkeiba.com"}:
            return 
        try:
            driver.get(self.url)
        except NonUrlError as e:
            return
        
        if "premium_new" in driver.current_url:
            domain = LoginForScraping.objects.get(domain=".netkeiba.com")
            domain.loggined = False
            domain.save()
            raise NonUrlError("ログインが必要です。")


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
        self.save_base(raw=True)


class PageOikiri(Page):
    html = models.BinaryField(null=True, blank=True)
    @property
    def url(self):
        if self.page_ptr.category.name == "nar.netkeiba.com":
            raise NonUrlError("nar.netkeiba.comには追い切りページがありません。")
        return f"https://race.netkeiba.com/race/oikiri.html?race_id={self.page_ptr.race_id}&type=2"

    @classmethod
    def need_cookie(cls):
        return True

    @cookie_required(".netkeiba.com")
    def update_html(self, driver):
        super().update_html(driver)


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
#             raise NonUrlError("race.netkeiba.comには枠単がありません。")
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