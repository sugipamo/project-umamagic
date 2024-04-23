from django.db import models
from selenium import webdriver
import pickle
import os
from time import perf_counter

class CookieForLogin(models.Model):
    domain = models.CharField(max_length=255)
    cookie_data = models.FileField(upload_to="cookies/")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


def cookie_required(domain):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not "driver" in kwargs:
                return func(*args, **kwargs)
            cookies = {}
            file = CookieForLogin.objects.filter(domain=domain)
            if not file.exists():
                file = CookieForLogin.objects.create(domain=domain)
            if file.first().cookie_data:
                with open(file.first().cookie_data.path, "rb") as f:
                    cookies = pickle.load(f)
            if type(cookies) != dict:
                cookies = {}
            if domain in cookies:
                kwargs["driver"].get("https://" + domain[1:] if domain.startswith(".") else "https://" + domain)
                [kwargs["driver"].add_cookie(cookie) for cookie in cookies[domain] if cookie["domain"] == domain]
            return_value = func(*args, **kwargs)
            with open(file.first().cookie_data.path, "wb") as f:
                pickle.dump(kwargs["driver"].get_cookies(), f)
            return return_value
            
        return wrapper
    return decorator


# withでつかってタイムアウトまでを計測する
class TimeCounter():
    def __init__(self):
        self.start = None
        self.end = None

    def __enter__(self, timeout=60):
        self.start = perf_counter()
        self.timeout = timeout
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.end = perf_counter()
        if self.end - self.start >= self.timeout:
            raise Exception("タイムアウトしました。")
        return True
    
    def get_time(self):
        return self.end - self.start
    
    def can_continue(self):
        return self.end - self.start < self.timeout

class WebDriver():
    def __init__(self):
        self.cookiepath = os.path.join("cookies.pkl")
        self.driver = webdriver.Remote(
            command_executor = os.environ["SELENIUM_URL"],
            options = webdriver.ChromeOptions()
        )

    def __enter__(self):
        return self.driver
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.driver.quit()
        if exc_type:
            raise exc_value
        return True