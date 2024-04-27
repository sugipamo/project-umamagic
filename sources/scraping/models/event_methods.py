from scraping.models.login_for_scraping import LoginForScraping
from scraping.models.webdriver import TimeCounter
from scraping.models.webdriver import cookie_required
from scraping.models.pages import RaceIdCategory, RaceId

class Test():
    def default_methods():
        pass

    def error_methods():
        raise Exception("エラーです。")

    def access_google(driver, url):
        driver.get(url)
        driver.find_elements("xpath", ".//a")[0].click()

    def save_google_html(driver, url):
        driver.get(url)
        from .html_documents import HtmlDocuments
        obj = HtmlDocuments.objects.create(url=url, html=driver.page_source)
        obj.delete()


class Login():
    def update_logined(driver):
        for domain in LoginForScraping.objects.filter(loggined=True):
            domain.update_logined(driver)

class NetKeiba():
    @cookie_required(".netkeiba.com")
    def collect_raceids(driver):
        with TimeCounter() as tc:
            elems = tc.do(driver.find_elements, "xpath", ".//a")
        elems = driver.find_elements("xpath", ".//a[contains(@href, 'race_id')]")
        urls = [elem.get_attribute("href") for elem in elems]
        url_categorys = {"jra": [], "nar": []}
        for url in urls:
            if "nar" in url:
                url_categorys["nar"].append(url)
            else:
                url_categorys["jra"].append(url)

        for url_category, urls in url_categorys.items():
            category = RaceIdCategory.objects.get_or_create(name=url_category)[0]
            for url in urls:
                params = url.split("?")[-1]
                params = dict([param.split("=") for param in params.split("&")])
                if "race_id" in params:
                    RaceId.objects.create(race_id=params["race_id"], category=category)

        