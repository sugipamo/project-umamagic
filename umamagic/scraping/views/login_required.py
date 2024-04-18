from django.shortcuts import render
from django.shortcuts import redirect
from django.http.response import HttpResponse
from ..forms.login_required import LoginRequiredDetailForm
from django.views.generic import ListView
from ..models.login_required import LoginRequired

class LoginRequiredListView(ListView):
    model = LoginRequired
    template_name = 'scraping/login_required_list.html'
    context_object_name = 'login_required_list'

def login_required_detail(request, pk):
    login_required = LoginRequired.objects.get(pk=pk)
    if request.method == 'POST':
        form = LoginRequiredDetailForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            login_required.login(username, password)
            return redirect('scraping:login_required_list')
        
    else:
        form = LoginRequiredDetailForm()
    return render(request, 'scraping/login_required_detail.html', {'login_required': login_required})

