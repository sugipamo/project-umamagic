from apps.web_controller.models import WebDriver
from os import environ

NETKEIBA_DOMAIN = ".netkeiba.com"

def login(self, **kwargs):
    url = "https://regist.netkeiba.com/account/?pid=login"
    environs = {}
    for v in ["NETKEIBA_USERNAME", "NETKEIBA_PASSWORD"]:
        if not v in environ:
            raise ValueError(f"{v} is not set in environ")
        environs[v] = kwargs.get(v, environ.get(v))
    with WebDriver(url=url, domain=NETKEIBA_DOMAIN) as driver:
        driver.find_element("name", "login_id").send_keys(environs["NETKEIBA_USERNAME"])
        driver.find_element("name", "pswd").send_keys(environs["NETKEIBA_PASSWORD"])
        driver.find_element("xpath", ".//div[@class='loginBtn__wrap']/input").click()
        if driver.find_elements("name", "login_id"):
            raise ValueError("Failed to login")
    return True

def update_logined(self):
    url = "https://user.sp.netkeiba.com/owner/prof.html"
    with WebDriver(url=url, domain=NETKEIBA_DOMAIN) as driver:
        loggined = url == driver.current_url

    if self.loggined != loggined:
        self.loggined = loggined
        self.save()
    return self.loggined