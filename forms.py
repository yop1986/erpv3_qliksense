from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from .models import TipoLicencia, Area, Area_TipoLicencia

class Area_TipoLicencia_ModelForm(forms.ModelForm):
    class Meta:
        model = Area_TipoLicencia
        fields = ['area', 'tipo', 'cantidad']
        #widgets = {'area': forms.HiddenInput()}
       
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        try:
            if(args and args[0]=='area'):
                self.fields['area'].queryset = self.fields['area'].queryset.filter(id=self.initial['area'])
                self.fields['area'].widget = forms.HiddenInput()
                excluidos = Area_TipoLicencia.objects.filter(area_id=self.initial['area']).values_list('tipo', flat=True)
                self.fields['tipo'].queryset = TipoLicencia.objects.exclude(id__in=excluidos)
            if(args and args[0] == 'tipo'):
                self.fields['tipo'].queryset = self.fields['tipo'].queryset.filter(id=self.initial['tipo'])
                self.fields['tipo'].widget = forms.HiddenInput()
                excluidos = Area_TipoLicencia.objects.filter(tipo_id=self.initial['tipo']).values_list('area', flat=True)
                self.fields['area'].queryset = Area.objects.exclude(id__in=excluidos)
        except:
            pass