from django.db import models
from scraping.models.webdriver import WebDriver
from selenium import webdriver
import pickle

COOKIEPATH = "cookies/"

class LoginForScraping(models.Model):
    domain = models.CharField(max_length=255)
    loggined = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.domain
    
    def login(self, username, password):
        with WebDriver() as driver:
            method = getattr(LoginMethods, self.domain.replace(".", ""))
            method(driver, username, password)
        self.loggined = True
        self.save()

    def update_logined(self, driver):
        method = getattr(LoginMethods, f"logined_{self.domain.replace('.', '')}")
        self.loggined = method(driver)
        self.save()

def cookie_required(domain):
    def decorator(func):
        def wrapper(*args, **kwargs):
            driver = [arg for arg in args if isinstance(arg, webdriver.Remote)]
            if not driver:
                return func(*args, **kwargs)
            else:
                driver = driver[0]
            cookies = {}
            import pathlib
            cookiepath = COOKIEPATH + "/" + domain + "_cookies.pkl"
            if pathlib.Path(cookiepath).exists():
                with open(cookiepath, "rb") as f:
                    cookies = pickle.load(f)
                if type(cookies) != list:
                    cookies = []
                url = "https://" + domain[1:] if domain.startswith(".") else "https://" + domain
                driver.get(url)
                [driver.add_cookie(cookie) for cookie in cookies]
            LoginForScraping.objects.get_or_create(domain=domain)
            return_value = func(*args, **kwargs)
            with open(cookiepath, "wb") as f:
                cookies = driver.get_cookies()
                cookies = [cookie for cookie in cookies if cookie["domain"] == domain]
                pickle.dump(cookies, f)
            return return_value
        return wrapper
    return decorator

class LoginMethods():
    @cookie_required(".google.com")
    def googlecom(driver, _, __):
        url = "https://www.google.com/"
        driver.get(url)
        
    @cookie_required(".google.com")
    def logined_googlecom(driver):
        url = "https://www.google.com/"
        driver.get(url)
        return False

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

