from django.db import models
from selenium import webdriver
import pickle
import os
from time import perf_counter
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

COOKIEPATH = "cookies/"
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
            return_value = func(*args, **kwargs)
            with open(cookiepath, "wb") as f:
                cookies = driver.get_cookies()
                cookies = [cookie for cookie in cookies if cookie["domain"] == domain]
                pickle.dump(cookies, f)
            return return_value
        return wrapper
    return decorator

# withでつかってタイムアウトまでを計測する
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
        return True
    
    @property
    def get_time(self):
        return perf_counter() - self.start
    
    def do(self, func, *args, **kwargs):
        """funcの戻り値がTrueになるまで実行する、タイムアウトしたらエラーを返す"""
        while True:
            result = func(*args, **kwargs)
            # print("result", result)
            if result:
                return result
            if self.get_time >= self.timeout:
                raise Exception("タイムアウトしました。")


class WebDriver():
    def __init__(self):
        self.cookiepath = os.path.join("cookies.pkl")
        options = webdriver.ChromeOptions()
        options.set_capability('pageLoadStrategy', 'eager')
        self.driver = webdriver.Remote(
            command_executor = os.environ["SELENIUM_URL"],
            options = options,
        )

    def __enter__(self):
        return self.driver
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.driver.quit()
        if exc_type:
            raise exc_type(exc_value).with_traceback(traceback)
        return True