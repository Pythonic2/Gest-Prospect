from django import forms

from gest_prospect.main import DEFAULT_QUERY

from .models import Prospect


class ImportProspectsForm(forms.Form):
    query = forms.CharField(label="Termo de busca", initial=DEFAULT_QUERY, max_length=500)
    limit = forms.IntegerField(label="Novos prospects", initial=30, min_value=1, max_value=60)


class ProspectStatusForm(forms.ModelForm):
    class Meta:
        model = Prospect
        fields = ("status",)
