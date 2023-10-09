from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.utils.translation import gettext as _
from django.urls import reverse_lazy

from usuarios.personal_views import (PersonalCreateView, PersonalUpdateView,
    PersonalListView, PersonalDetailView, PersonalDeleteView,
    Configuraciones)

from .models import TipoLicencia

gConfiguracion = Configuraciones()
DISPLAYS = {
    'forms': {
        'submit': _('Guardar'),
        'cancel': _('Cancelar'),
    },
    'opciones': {
        'detail': _('Ver'),
        'update': _('Editar'),
        'delete': _('Eliminar'),
    }
}


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
    permission_required = 'qliksense.view_tipolicencias'
    template_name = 'qliksense/lists.html'
    model = TipoLicencia
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

    def get_context_data(self):
        context = super().get_context_data()
        print(context)
        return context

class LicenciasCreateView(PersonalCreateView):
    permission_required = 'qliksense.view_tipolicencias'
    template_name = 'qliksense/forms.html'
    model = TipoLicencia
    fields = ['descripcion', 'cantidad']
    success_url = reverse_lazy('qliksense:list_licencia')
    extra_context = {
        'title': _('Nuevo tipo de licencia'),
        'opciones': DISPLAYS['forms'],
    }

class LicenciasDetailView(PersonalDetailView):
    pass

class LicenciasUpdateView(PersonalUpdateView):
    permission_required = 'qliksense.change_tipolicencia'
    template_name = 'qliksense/forms.html'
    model = TipoLicencia
    fields = ['descripcion', 'cantidad']
    success_url = reverse_lazy('qliksense:detail_licencia')
    extra_context = {
        'title': _('Modificar tipo de licencia'),
        'opciones': DISPLAYS['forms'],
    }

class LicenciasDeleteView(PersonalDeleteView):
    pass