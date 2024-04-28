from scraping.models.login_for_scraping import LoginForScraping

def update_logined(driver):
    for domain in LoginForScraping.objects.filter(loggined=True):
        domain.update_logined(driver)
