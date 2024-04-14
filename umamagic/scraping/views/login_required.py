from django.shortcuts import render
from django.http.response import HttpResponse
from ..forms.login_required import LoginRequiredForm

def login_required_form(request):
    if request.method == "POST":
        form = LoginRequiredForm(request.POST)
        if form.is_valid():
            return HttpResponse("ログイン成功")
    else:
        form = LoginRequiredForm()
    return render(request, 'scraping/login_required.html', {'form': form})