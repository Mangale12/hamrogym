from django import forms

from core.models.curency import Currency

class CurrencyForm(forms.ModelForm):
    class Meta:
        model = Currency
        fields = ['code', 'name', 'symbol']
