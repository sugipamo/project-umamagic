# views.py
from django.shortcuts import render, redirect
from .forms import LoginForScrapingDetailForm
from .models import LoginForScraping
from django.views.generic import ListView
from pathlib import Path


class LoginForScrapingListView(ListView):
    model = LoginForScraping
    template_name = 'web_controller/login_for_scraping_list.html'
    context_object_name = 'login_for_scraping_list'

    def get_queryset(self):
        existing_domains = set(LoginForScraping.objects.values_list('domain', flat=True))
        # 新しい要素をデータベースに追加する
        for f in Path(__file__).parent.glob('login_methods/*.py'):
            domain = f.with_suffix("").name.replace("_", ".")
            if domain not in existing_domains:
                LoginForScraping.objects.create(domain=domain)

        return LoginForScraping.objects.all()

def login_for_scraping_detail(request, pk):
    login_for_scraping = LoginForScraping.objects.get(pk=pk)
    if request.method == 'POST':
        form = LoginForScrapingDetailForm(request.POST)
        if form.is_valid():
            login_for_scraping.login(**form.cleaned_data)
            return redirect('web_controller:login_for_scraping_list')
        
    else:
        form = LoginForScrapingDetailForm()
    return render(request, 'web_controller/login_for_scraping_detail.html', {'login_for_scraping': login_for_scraping})