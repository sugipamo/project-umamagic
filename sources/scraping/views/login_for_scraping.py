from django.shortcuts import render
from django.shortcuts import redirect
from django.http.response import HttpResponse
from ..forms.login_for_scraping import LoginForScrapingDetailForm
from django.views.generic import ListView
from ..models.login_for_scraping import LoginForScraping

class LoginForScrapingListView(ListView):
    model = LoginForScraping
    template_name = 'scraping/login_for_scraping_list.html'
    context_object_name = 'login_for_scraping_list'

def login_for_scraping_detail(request, pk):
    login_for_scraping = LoginForScraping.objects.get(pk=pk)
    if request.method == 'POST':
        form = LoginForScrapingDetailForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            login_for_scraping.login(username, password)
            return redirect('scraping:login_for_scraping_list')
        
    else:
        form = LoginForScrapingDetailForm()
    return render(request, 'scraping/login_for_scraping_detail.html', {'login_for_scraping': login_for_scraping})

