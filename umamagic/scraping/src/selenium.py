from selenium import webdriver
import os

def save_html(driver, path):
    with open(path, "w") as f:
        f.write(driver.page_source)

class WebDriver():
    def __init__(self):
        self.driver = webdriver.Remote(
            command_executor = os.environ["SELENIUM_URL"],
            options = webdriver.ChromeOptions()
        )
        self.driver.save_html = lambda path: save_html(self.driver, path)
    
    def __enter__(self):
        return self.driver
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.driver.quit()
        if exc_type:
            raise exc_value
        return True