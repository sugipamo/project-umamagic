from django.db import models
from importlib import import_module

class LoginForScraping(models.Model):
    domain = models.CharField(max_length=255)
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



