from django.db import models
from .webdriver import cookie_required

class LoginMethods():
    @cookie_required(".netkeiba.com")
    def netkeibacom(driver, username, password):
        url = "https://regist.netkeiba.com/account/?pid=login"
        driver.get(url)
        url = driver.current_url
        driver.find_element("name", "login_id").send_keys(username)
        driver.find_element("name", "pswd").send_keys(password)
        driver.find_element("xpath", ".//div[@class='loginBtn__wrap']/input").click()
        if driver.find_elements("name", "login_id"):
            raise Exception("ログインに失敗しました。")
        
    @cookie_required(".netkeiba.com")
    def logined_netkeibacom(driver):
        url = "https://user.sp.netkeiba.com/owner/prof.html"
        driver.get(url)
        if url == driver.current_url:
            return True
        return False


class LoginForScraping(models.Model):
    domain = models.CharField(max_length=255)
    loggined = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.domain
    
    def login(self, username, password):
        method = getattr(LoginMethods, self.domain.replace(".", ""))
        from .webdriver import WebDriver
        with WebDriver() as driver:
            method(driver, username, password)

        self.loggined = True
        self.save()

    def is_logined(self):
        method = getattr(LoginMethods, f"logined_{self.domain.replace('.', '')}")
        from .webdriver import WebDriver
        with WebDriver() as driver:
            return method(driver)