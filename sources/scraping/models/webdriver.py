from selenium import webdriver
import os
from time import perf_counter

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