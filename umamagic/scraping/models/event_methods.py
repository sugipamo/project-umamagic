import pickle
import os
from .webdriver import login_required

class Test():
    def default_methods():
        pass

    def error_methods():
        raise Exception("エラーです。")

    def access_google(driver, url):
        driver.get(url)
        driver.find_elements("xpath", ".//a")[0].click()

    def save_google_html(driver, url):
        driver.get(url)
        from .html_documents import HtmlDocuments
        obj = HtmlDocuments.objects.create(url=url, html=driver.page_source)
        obj.delete()


class LoginInfo():
    @login_required(".netkeiba.com")
    def netkeiba(driver, url, username = "", password = ""):
        driver.get(url)
        url = driver.current_url
        if username == "":
            username = input("ユーザー名を入力してください: ")
        driver.find_element("name", "login_id").send_keys(username)
        if password == "":
            from getpass import getpass
            password = getpass("パスワードを入力してください: ")
        driver.find_element("name", "pswd").send_keys(password)
        driver.find_element("xpath", ".//div[@class='loginBtn__wrap']/input").click()
        if driver.find_elements("name", "login_id"):
            raise Exception("ログインに失敗しました。")
        
        from time import sleep
        sleep(3)