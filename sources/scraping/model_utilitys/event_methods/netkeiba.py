from scraping.models.login_for_scraping import cookie_required
from scraping.models.pages import RaceCategory, Race
from scraping.model_utilitys.webdriver import TimeCounter

def extract_raceids(driver):
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

    ret = {}
    for url_category, urls in url_categorys.items():
        category = RaceCategory.objects.get_or_create(name=url_category)[0]
        if category not in ret:
            ret[category] = []
        for url in urls:
            params = url.split("?")[-1]
            params = dict([param.split("=") for param in params.split("&")])
            if "race_id" in params:
                ret[category].append(params["race_id"])

            for category in ret:
                ret[category] = list(set(ret[category]))
    
    return ret

@cookie_required(".netkeiba.com")
def new_raceids(driver):
    for url in ["https://race.netkeiba.com/top/", "https://nar.netkeiba.com/top/"]:
        driver.get(url)
        for category, raceids in extract_raceids(driver).items():
            for raceid in raceids:
                Race.objects.get_or_create(race_id=raceid, category=category)