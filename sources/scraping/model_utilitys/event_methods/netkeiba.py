from scraping.models.login_for_scraping import cookie_required
from scraping.models.netkeiba_pages import PageCategory, Page
from scraping.models.netkeiba_pages import Pages
from scraping.model_utilitys.webdriver import TimeCounter



def extract_raceids(driver):
    with TimeCounter() as tc:
        elems = tc.do(driver.find_elements, "xpath", ".//a")
    elems = driver.find_elements("xpath", ".//a[contains(@href, 'race_id')]")
    urls = {elem.get_attribute("href") for elem in elems}

    raceids = {}
    race_categorys = {}
    for url in urls:
        race_category = url.split("/")[2]
        category = race_categorys.get(race_category, PageCategory.objects.get_or_create(name=race_category)[0])
        params = url.split("?")[-1]
        params = dict([param.split("=") for param in params.split("&")])
        if "race_id" in params:
            race_id = params["race_id"]
            if race_id not in raceids:
                raceids[race_id] = Page.objects.get_or_create(race_id=race_id, category=category)[0]
                
# @cookie_required(".netkeiba.com")
def new_raceids(driver):
    for url in ["https://race.netkeiba.com/top/", "https://nar.netkeiba.com/top/"]:
        driver.get(url)
        extract_raceids(driver)


def new_page(driver):
    models = Pages.PageClasses
    model = min(models, key=lambda m: m.objects.exclude(html=None).count())
    race = model.next_raceid()
    if race is None:
        return
    race.update_html(driver)
    extract_raceids(driver)

    return race
