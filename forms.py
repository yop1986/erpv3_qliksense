from django import forms
from django.core.exceptions import ValidationError
from django.db.models import F, Count
from django.utils.translation import gettext as _

from .models import TipoLicencia, Area, Area_TipoLicencia, Usuario

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

class UsuarioCreate_ModelForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['tipo', 'codigo', 'nombre', 'extension', 'correo', 'area_tipo']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            # Se excluyen las areas_tipo que llegaron al limite de la cantidad de licencias
            # de las cuales disponen
            excluidos = Usuario.objects.filter(vigente=True).values('area_tipo')\
                .annotate(licencias_usadas=Count('id'))\
                .filter(licencias_usadas__gte=F('area_tipo__cantidad'))\
                .values_list('area_tipo', flat=True)
            self.fields['area_tipo'].queryset = self.fields['area_tipo'].queryset\
                .order_by('area__nombre', 'tipo__descripcion').exclude(id__in=excluidos)
        except: 
            pass 

class UsuarioUpdate_ModelForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['tipo', 'codigo', 'nombre', 'extension', 'correo', 'area_tipo', 'vigente']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            # Se excluyen las areas_tipo que llegaron al limite de la cantidad de licencias
            # de las cuales disponen (se excluye de esto la que esta actualmente asignada
            # al usuario que se modifica)
            excluidos = Usuario.objects.filter(vigente=True)\
                .exclude(area_tipo=self.initial['area_tipo']).values('area_tipo')\
                .annotate(licencias_usadas=Count('id'))\
                .filter(licencias_usadas__gte=F('area_tipo__cantidad'))\
                .values_list('area_tipo', flat=True)
            self.fields['area_tipo'].queryset = self.fields['area_tipo'].queryset\
                .order_by('area__nombre', 'tipo__descripcion').exclude(id__in=excluidos)
        except: 
            pass 