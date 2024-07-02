# urls.py
from django.urls import path
from web_controller import views
from django.views.generic import TemplateView

app_name = 'web_controller'
urlpatterns = [
    path('login_success/', TemplateView.as_view(template_name='login_success.html'), name='login_success'),
    path('login_for_scraping_form/', views.login_for_scraping_detail, name='login_for_scraping_form'),
    path('login_for_scraping_list/', views.LoginForScrapingListView.as_view(), name='login_for_scraping_list'),
    path('login_for_scraping_detail/<int:pk>/', views.login_for_scraping_detail, name='login_for_scraping_detail'),
]
