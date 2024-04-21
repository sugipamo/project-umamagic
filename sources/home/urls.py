from django.urls import path
from . import views

# https://noauto-nolife.com/post/django-auto-create-all-apps-link/

app_name    = "home"
urlpatterns = [
    path("", views.index, name="index"),
]
