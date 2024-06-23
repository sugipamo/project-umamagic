
# class LoginForScraping(models.Model):
#     domain = models.CharField(max_length=255)
#     loggined = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return self.domain
    
#     @abc.abstractmethod
#     def login_method(self, driver):
#         pass

#     @abc.abstractmethod
#     def update_logined_method(self, driver):
#         pass

#     def login(self, *args, **kwargs):
#         with WebDriver() as driver:
#             self.login_method(driver, *args, **kwargs)

#         self.loggined = True
#         self.save()

#     def update_logined(self, driver):
#         with WebDriver() as driver:
#             loggined = self.update_logined_method(driver)

#         if self.loggined != loggined:
#             self.loggined = loggined
#             self.save()
#         return self.loggined



