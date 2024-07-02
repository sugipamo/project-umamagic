from django.apps import AppConfig
from selenium import webdriver
from time import sleep, perf_counter
import pickle
import os
from pathlib import Path

class WebControllerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'web_controller'


COOKIEPATH = Path(__file__).parent / "cookies"
if not COOKIEPATH.exists():
    COOKIEPATH.mkdir()

class TimeCounter():
    def __init__(self):
        self.start = perf_counter()

    def __enter__(self, timeout=60):
        self.start = perf_counter()
        self.timeout = timeout
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        if self.get_time >= self.timeout:
            raise Exception("タイムアウトしました。")
    
    @property
    def get_time(self):
        return perf_counter() - self.start
    
    def do(self, func, *args, **kwargs):
        """funcの戻り値がTrueになるまで実行する、タイムアウトしたらエラーを返す"""
        while True:
            result = func(*args, **kwargs)
            if result:
                return result
            if self.get_time >= self.timeout:
                raise Exception("タイムアウトしました。")
            sleep(1)

class WebDriver():
    def __init__(self, *args, pageLoadStrategy="eager", **kwargs):
        options = webdriver.ChromeOptions()
        options.set_capability('pageLoadStrategy', pageLoadStrategy)
        self.driver = webdriver.Remote(
            command_executor=os.environ["SELENIUM_URL"],
            options=options,
        )
        self.quit_functions = []

        if "url" in kwargs:
            self.driver.get(kwargs["url"])

        if "domain" in kwargs and type(kwargs["domain"]) == str:
            kwargs["domain"] = [kwargs["domain"]]

        for domain in kwargs.get("domain", []):
            self.__cookie_init(domain)

    def __cookie_init(self, domain):
        self.cookiepath = COOKIEPATH / (domain + "_cookies.pkl")
        if not self.cookiepath.exists():
            return
        
        if not domain in self.driver.current_url:
            self.driver.get(domain)

        with open(self.cookiepath, "rb") as f:
            cookies = pickle.load(f)

        if type(cookies) != list:
            cookies = []

        for cookie in cookies:
            if cookie["domain"] == domain:
                self.driver.add_cookie(cookie)

        self.quit_functions.append(lambda :self.__cookie_save(domain))

    def __cookie_save(self, domain):
        with open(self.cookiepath, "wb") as f:
            cookies = self.driver.get_cookies()
            cookies = [cookie for cookie in cookies if cookie["domain"] == domain]
            pickle.dump(cookies, f)

    def __enter__(self):
        return self.driver
    
    def __exit__(self, exc_type, exc_value, traceback):
        for func in self.quit_functions:
            func()
        self.driver.quit()