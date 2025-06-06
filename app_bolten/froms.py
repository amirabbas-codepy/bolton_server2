
from django import forms

class LoginForm(forms.Form):
    email = forms.EmailField(required=True)
    # phone = forms.CharField(max_length=20, required=True)

class TraketForm(forms.Form):
    keyword = forms.CharField(max_length=250)
    frequency_days = forms.IntegerField()

class DeletedForm(forms.Form):
    news_id = forms.IntegerField(required=True)

class SearchForm(forms.Form):
    value = forms.CharField(max_length=300, label='keyword')