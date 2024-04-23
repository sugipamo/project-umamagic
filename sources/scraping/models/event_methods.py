from scraping.models.login_for_scraping import LoginForScraping
from scraping.models.webdriver import TimeCounter

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
    def update_logined():
        for domain in LoginForScraping.objects.filter(loggined=True):
            domain.update_logined()

class NetKeiba():
    def collect_raceids(driver):
        driver.get("https://race.netkeiba.com/top/?rf=navi")
        with TimeCounter() as tc:
            while tc.can_continue():
                elems = driver.find_elements("xpath", ".//div[@class='RaceList_Area']")
                if elems:
                    break
        print(elems)
        