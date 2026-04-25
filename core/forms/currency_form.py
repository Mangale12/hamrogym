from django import forms

from nepanest.foundation.fiscal import Currency

class CurrencyForm(forms.ModelForm):
    class Meta:
        model = Currency
        fields = ['code', 'name', 'symbol']
