from selenium import webdriver
import pickle
import os
import pathlib

def login_required(domain):
    def decorator(func):
        def wrapper(*args, **kwargs):
            cookies = {}
            if "driver" in kwargs:
                if pathlib.Path("cookies.pkl").exists():
                    with open("cookies.pkl", "rb") as f:
                        cookies = pickle.load(f)
                    if type(cookies) != dict:
                        cookies = {}
                    if domain in cookies:
                        kwargs["driver"].get("https://" + domain[1:] if domain.startswith(".") else "https://" + domain)
                        [kwargs["driver"].add_cookie(cookie) for cookie in cookies[domain] if cookie["domain"] == domain]
            return_value = func(*args, **kwargs)
            if "driver" in kwargs:
                with open("cookies.pkl", "wb") as f:
                    pickle.dump({**cookies, **{domain: kwargs["driver"].get_cookies()}}, f)
            return return_value
        return wrapper
    return decorator

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