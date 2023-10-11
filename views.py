from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views.generic.edit import FormMixin

from usuarios.personal_views import (PersonalCreateView, PersonalUpdateView,
    PersonalListView, PersonalDetailView, PersonalDeleteView, PersonalFormView,
    Configuraciones)

from .models import TipoLicencia, Area, Area_TipoLicencia
from .forms import Area_TipoLicencia_CreateForm

gConfiguracion = Configuraciones()
DISPLAYS = {
    'forms': {
        'submit': _('Guardar'),
        'cancel': _('Cancelar'),
    },
    'delete_form': {
        'submit': _('Eliminar'),
        'cancel': _('Cancelar'),
    },
    'opciones': {
        'detail': _('Ver'),
        'update': _('Editar'),
        'delete': _('Eliminar'),
    },
    'confirmacion': _('¿Esta seguro de eliminar el elemento indicado?')
}

### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### 
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### 
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### 

class IndexTemplateView(TemplateView):
    template_name = 'qliksense/index.html'

    extra_context ={
        'title': _('Qlik Sense'),
        'general': {
            'nombre_sitio': gConfiguracion.get_value('sitio', 'nombre'),
        },
        'elementos': [
            {
                'display':  _('Licencias'),
                'desc':     _('Control de licencias disponibles en la \
                    aplicación'),
                'imagen':   _('qs_licencias.png'),
            },
            {
                'display':  _('Asignacion de áreas'),
                'desc':     _('Asignación de licencias por área encargada.'),
                'imagen':   _('qs_areas.png'),
            },
            {
                'display':  _('Usuarios'),
                'desc':     _('Asignación de licencias por usuario'),
                'imagen':   _('qs_usuarios.png'),
            },
            {
                'display':  _('Permisos por Stream'),
                'desc':     _('Gestión general de los permisos a cada uno de \
                    los usuarios por stream.'),
                'imagen':   _('qs_permisos_stream.png'),
            },            {                'display':  _('Stream'),
                'desc':     _('Listado de streams definidios en la aplciación \
                    (generado de forma automático al conectarse con la api de \
                    Qlik Sense).'),
                'imagen':   _('qs_stream.png'),
            },
            {
                'display':  _('Modelos'),
                'desc':     _('Gestión general de los permisos a cada uno de \
                    los usuarios por stream.'),
                'imagen':   _('qs_modelos.png'),
            },
        ],
    }


class LicenciasListView(PersonalListView):
    permission_required = 'qliksense.view_tipolicencia'
    template_name = 'qliksense/list.html'
    model = TipoLicencia
    ordering = ['descripcion']
    extra_context = {
        'title': _('Licencias'),
        'campos': {
            #-1: no enumera
            # 0: inicia numeración en 0
            # 1: inicia numeración en 1
            'enumerar': 1,
            # Si hay valor se muestra opciones por linea, de lo contrario no se muestran
            'opciones': _('Opciones'),
            # Lista de campos que se deben mostrar en la tabla
            'lista': [
                'descripcion', 
                'cantidad', 
            ],
        },
        'opciones': DISPLAYS['opciones'],
        'mensaje': {
            'vacio': _('No hay elementos para mostrar.'),
        },
    }

class LicenciasCreateView(PersonalCreateView):
    permission_required = 'qliksense.add_tipolicencia'
    template_name = 'qliksense/forms.html'
    model = TipoLicencia
    fields = ['descripcion', 'cantidad']
    success_url = reverse_lazy('qliksense:list_licencia')
    extra_context = {
        'title': _('Nuevo tipo de licencia'),
        'opciones': DISPLAYS['forms'],
    }

class LicenciasDetailView(PersonalDetailView):
    permission_required = 'qliksense.view_tipolicencia'
    template_name = 'qliksense/detail.html'
    model = TipoLicencia
    extra_context = {
        'title': _('Tipo'),
        'campos': {
            'opciones': _('Opciones'),
            'lista': [
                #'id',
                'descripcion', 
                'cantidad', 
            ],
        },
        'opciones': DISPLAYS['opciones'],
    }

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['campos_adicionales'] = [ 
            {'display': _('Licencias asignadas'), 'valor': self.object.licencias_asignadas()},
            {'display': _('Licencias pendientes'), 'valor': self.object.licencias_no_asignadas()},
        ]
        return context

class LicenciasUpdateView(PersonalUpdateView):
    permission_required = 'qliksense.change_tipolicencia'
    template_name = 'qliksense/forms.html'
    model = TipoLicencia
    fields = ['descripcion', 'cantidad']
    extra_context = {
        'title': _('Modificar tipo de licencia'),
        'opciones': DISPLAYS['forms'],
    }

    def get_success_url(self):
        return self.object.url_detail()

class LicenciasDeleteView(PersonalDeleteView):
    permission_required = 'qliksense.delete_tipolicencia'
    template_name = 'qliksense/delete_confirmation.html'
    model = TipoLicencia
    success_url = reverse_lazy('qliksense:list_licencia')
    extra_context = {
        'title': _('Eliminar tipo de licencia'),
        'confirmacion': DISPLAYS['confirmacion'],
        'opciones': DISPLAYS['delete_form'],
    }


class AreaListView(PersonalListView):
    permission_required = 'qliksense.view_area'
    template_name = 'qliksense/list.html'
    model = Area
    ordering = ['nombre']
    extra_context = {
        'title': _('Areas'),
        'campos': {
            #-1: no enumera
            # 0: inicia numeración en 0
            # 1: inicia numeración en 1
            'enumerar': 1,
            # Si hay valor se muestra opciones por linea, de lo contrario no se muestran
            'opciones': _('Opciones'),
            # Lista de campos que se deben mostrar en la tabla
            'lista': [
                'nombre', 
            ],
        },
        'opciones': DISPLAYS['opciones'],
        'mensaje': {
            'vacio': _('No hay elementos para mostrar.'),
        },
    }

class AreaCreateView(PersonalCreateView):
    permission_required = 'qliksense.add_area'
    template_name = 'qliksense/forms.html'
    model = Area
    fields = ['nombre']
    extra_context = {
        'title': _('Area/Gerencia'),
        'opciones': DISPLAYS['forms'],
    }

    def get_success_url(self):
        return self.object.url_detail()

class AreaDetailView(PersonalDetailView):
    permission_required = 'qliksense.view_area'
    template_name = 'qliksense/detail.html'
    model = Area
    extra_context = {
        'title': _('Area / Gerencia'),
        'campos': {
            'opciones': _('Opciones'),
            'lista': [
                'nombre' 
            ],
        },
        'opciones': DISPLAYS['opciones'],
    }

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['forms'] = [
            {
                'modal':    'area_tipolicencia', 
                'action':   reverse_lazy('qliksense:create_areatipo'),
                'display':  _('Asignación de licencias'),
                'form':     Area_TipoLicencia_CreateForm(instance=Area_TipoLicencia(area=self.object)),
                'opciones': DISPLAYS['forms'],
            },
        ]
        return context


class AreaUpdateView(PersonalUpdateView):
    permission_required = 'qliksense.change_area'
    template_name = 'qliksense/forms.html'
    model = Area
    fields = ['nombre']
    extra_context = {
        'title': _('Modificar área / gerencia'),
        'opciones': DISPLAYS['forms'],
    }

    def get_success_url(self):
        return self.object.url_detail()

class AreaDeleteView(PersonalDeleteView):
    permission_required = 'qliksense.delete_area'
    template_name = 'qliksense/delete_confirmation.html'
    model = Area
    success_url = reverse_lazy('qliksense:list_area')
    extra_context = {
        'title': _('Eliminar area / gerencia'),
        'confirmacion': DISPLAYS['confirmacion'],
        'opciones': DISPLAYS['delete_form'],
    }




class Area_TipoLicenciaCreateView(PersonalFormView):
    permission_required = 'qliksense.add_area_tipolicencia'
    template_name = 'qliksense/forms.html'
    model = Area_TipoLicencia
    form_class = Area_TipoLicencia_CreateForm
    #success_url =
    success_message = 'Asignación exitosa'

    def form_valid(self, form, *args, **kwargs):
        data = form.cleaned_data
        area_tipo = Area_TipoLicencia(**data)
        area_tipo.save()
        self.success_url = area_tipo.url_parent_detail()
        return super().form_valid(form)