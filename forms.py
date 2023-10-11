from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from .models import TipoLicencia, Area_TipoLicencia

class Area_TipoLicencia_CreateForm(forms.ModelForm):
    class Meta:
        model = Area_TipoLicencia
        fields = ['area', 'tipo', 'cantidad']
        widgets = {'area': forms.HiddenInput()}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            tipo_excluidos = Area_TipoLicencia.objects.filter(area_id=self.initial['area']).values_list('tipo', flat=True)
            self.fields['tipo'].queryset = TipoLicencia.objects.exclude(id__in=tipo_excluidos)
        except:
            pass