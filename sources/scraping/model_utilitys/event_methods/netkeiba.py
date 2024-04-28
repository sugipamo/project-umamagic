from scraping.models.login_for_scraping import cookie_required
from scraping.models.pages import RaceCategory, Race, Shutuba
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
        category = race_categorys.get(race_category, RaceCategory.objects.get_or_create(name=race_category)[0])
        params = url.split("?")[-1]
        params = dict([param.split("=") for param in params.split("&")])
        if "race_id" in params:
            if params["race_id"] not in raceids:            
                raceids[params["race_id"]] = Race.objects.get_or_create(race_id=params["race_id"], category=category)

    return raceids

# @cookie_required(".netkeiba.com")
def new_raceids(driver):
    for url in ["https://race.netkeiba.com/top/", "https://nar.netkeiba.com/top/"]:
        driver.get(url)
        extract_raceids(driver)


def new_shutuba(driver):
    races = Shutuba.get_unused_raceids()
    if not races:
        return
    race = races.first()
    shutuba = Shutuba.objects.get_or_create(race=race)[0]
    shutuba.update_html(driver)
    