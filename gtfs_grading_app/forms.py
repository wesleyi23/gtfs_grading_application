from django import forms


class GtfsZipForm(forms.Form):
    file = forms.FileField()