from django import forms

from gest_prospect.main import DEFAULT_QUERY

from .models import Prospect


class ImportProspectsForm(forms.Form):
    query = forms.CharField(label="Termo de busca", initial=DEFAULT_QUERY, max_length=500)
    segment = forms.CharField(
        label="Segmento para cadastrar",
        max_length=120,
        help_text="Escolha um segmento existente ou digite um novo.",
        widget=forms.TextInput(attrs={"list": "segment-suggestions", "placeholder": "Ex.: Logística"}),
    )
    limit = forms.IntegerField(label="Novos prospects", initial=30, min_value=1, max_value=60)

    def clean_segment(self):
        return " ".join(self.cleaned_data["segment"].split())


class ProspectStatusForm(forms.ModelForm):
    class Meta:
        model = Prospect
        fields = ("status",)
