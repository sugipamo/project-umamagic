from django.db import models
from importlib import import_module
from selenium import webdriver
import os
import logging
from time import sleep, perf_counter

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        # WebDriverのオプションを設定
        options = webdriver.ChromeOptions()
        options.set_capability('pageLoadStrategy', pageLoadStrategy)
        self.driver = webdriver.Remote(
            command_executor=os.environ["SELENIUM_URL"],
            options=options,
        )
        self.quit_functions = []

        # 初期化時に指定されたURLを開く
        if "url" in kwargs:
            try:
                self.driver.get(kwargs["url"])
            except Exception as e:
                logger.warning(f"Failed to load initial URL: {kwargs['url']}. Error: {e}")

        # ドメインごとにクッキーを初期化
        if "domain" in kwargs and isinstance(kwargs["domain"], str):
            kwargs["domain"] = [kwargs["domain"]]

        for domain in kwargs.get("domain", []):
            self.__cookie_init(domain)
        
        # URLを再度取得（クッキー設定後のアクセスを保証）
        if "url" in kwargs:
            self.driver.get(kwargs["url"])

    def __cookie_init(self, domain):
        """
        指定されたドメインに対して保存されたクッキーを読み込んでWebDriverに適用
        """
        self.quit_functions.append(lambda: self.__cookie_save(domain))  # セッション終了時にクッキーを保存
        cookies = LoginForScraping.objects.filter(domain=domain).first()
        if cookies is None:
            logger.info(f"No cookies found for domain: {domain}")
            return

        cookies = cookies.cookie
        if not isinstance(cookies, list):
            logger.warning(f"Invalid cookies format for domain: {domain}. Expected list, got {type(cookies)}")
            cookies = []

        # クッキーを適用
        for cookie in cookies:
            if self.__is_valid_cookie(cookie) and self.__is_same_or_subdomain(domain, cookie["domain"]):
                try:
                    self.driver.add_cookie(cookie)
                    # logger.info(f"Added cookie: {cookie}")
                except Exception as e:
                    logger.error(f"Failed to add cookie: {cookie}. Error: {e}")
            else:
                logger.warning(f"Skipped invalid or non-matching cookie: {cookie}")

    def __cookie_save(self, domain):
        """
        指定されたドメインに対するクッキーを取得して保存
        """
        cookies = self.driver.get_cookies()
        filtered_cookies = [cookie for cookie in cookies if self.__is_same_or_subdomain(domain, cookie["domain"])]
        login, _ = LoginForScraping.objects.get_or_create(domain=domain)
        login.cookie = filtered_cookies
        login.save()
        logger.info(f"Saved cookies for domain: {domain}")

    @staticmethod
    def __is_valid_cookie(cookie):
        """
        クッキーの形式を検証
        """
        required_keys = {"name", "value", "domain", "path"}  # 必須フィールド
        return isinstance(cookie, dict) and required_keys.issubset(cookie.keys())

    @staticmethod
    def __is_same_or_subdomain(domain, cookie_domain):
        """
        ドメインの一致またはサブドメインの判定
        """
        return cookie_domain == domain or cookie_domain.endswith(f".{domain}")


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



