from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from time import sleep, perf_counter
import os
class DriverNotExistsError(Exception):
    pass

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
    def __init__(self, pageLoadStrategy="eager"):
        options = webdriver.ChromeOptions()
        options.set_capability('pageLoadStrategy', pageLoadStrategy)
        self.driver = webdriver.Remote(
            command_executor=os.environ["SELENIUM_URL"],
            options=options,
        )

    def __enter__(self):
        return self.driver
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.driver.quit()