from apps.web_controller.apps import  WebDriver

NETKEIBA_DOMAIN = ".netkeiba.com"

def login(self, **kwargs):
    url = "https://regist.netkeiba.com/account/?pid=login"
    username = kwargs.get("username")
    password = kwargs.get("password")
    with WebDriver(url=url, domain=NETKEIBA_DOMAIN) as driver:
        driver.find_element("name", "login_id").send_keys(username)
        driver.find_element("name", "pswd").send_keys(password)
        driver.find_element("xpath", ".//div[@class='loginBtn__wrap']/input").click()
        if driver.find_elements("name", "login_id"):
            return False
    return True

def update_logined(self):
    url = "https://user.sp.netkeiba.com/owner/prof.html"
    with WebDriver(url=url, domain=NETKEIBA_DOMAIN) as driver:
        loggined = url == driver.current_url

    if self.loggined != loggined:
        self.loggined = loggined
        self.save()
    return self.loggined