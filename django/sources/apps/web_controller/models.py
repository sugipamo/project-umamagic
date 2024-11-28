from django.db import models
from importlib import import_module
from selenium import webdriver
import os
from time import sleep, perf_counter

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
            try:
                self.driver.get(kwargs["url"])
            except:
                pass

        if "domain" in kwargs and type(kwargs["domain"]) == str:
            kwargs["domain"] = [kwargs["domain"]]

        for domain in kwargs.get("domain", []):
            self.__cookie_init(domain)

    def __cookie_init(self, domain):
        self.quit_functions.append(lambda :self.__cookie_save(domain))
        cookies = LoginForScraping.objects.filter(domain=domain).first()
        if cookies is None:
            return
        cookies = cookies.cookie
        if type(cookies) != list:
            cookies = []

        for cookie in cookies:
            if cookie["domain"] == domain:
                self.driver.add_cookie(cookie)

    def __cookie_save(self, domain):
        cookies = self.driver.get_cookies()
        cookies = [cookie for cookie in cookies if cookie["domain"] == domain]
        login = LoginForScraping.objects.get_or_create(domain=domain)
        login = login[0]
        login.cookie = cookies
        login.save()

    def __enter__(self):
        return self.driver
    
    def __exit__(self, exc_type, exc_value, traceback):
        for func in self.quit_functions:
            func()
        self.driver.quit()

class LoginForScraping(models.Model):
    domain = models.CharField(max_length=255)
    cookie = models.JSONField(default=list)
    loggined = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.domain
    
    def login(self, **kwargs):
        login_method = import_module("apps.web_controller.login_methods.{}".format(self.domain.replace(".", "_")))
        self.loggined = login_method.login(self, **kwargs)
        self.save()

    def update_logined(self, driver):
        login_method = import_module("apps.web_controller.login_methods.{}".format(self.domain.replace(".", "_")))
        loggined = login_method.update_logined(self)

        if self.loggined != loggined:
            self.loggined = loggined
            self.save()
        return self.loggined



