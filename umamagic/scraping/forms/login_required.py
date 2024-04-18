from django import forms

class LoginRequiredDetailForm(forms.Form):
    username = forms.CharField(label='ユーザー名', max_length=255)
    password = forms.CharField(label='パスワード', max_length=255, widget=forms.PasswordInput)
