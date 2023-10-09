from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.utils.translation import gettext as _

from usuarios.personal_views import (PersonalCreateView, PersonalUpdateView,
    PersonalListView, PersonalDetailView, PersonalDeleteView)

class IndexTemplateView(TemplateView):
    template_name = 'qliksense/index.html'

    extra_context ={
        'title': _('Qlik Sense'),
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
                    los usuarios por stream.'),                'iagen':   _('qs_permisos_stream.png'),
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
    pass

class LicenciasCreateView(PersonalCreateView):
    pass

class LicenciasUpdateView(PersonalUpdateView):
    pass

class LicenciasDetailView(PersonalDetailView):
    pass

class LicenciasDeleteView(PersonalDeleteView):
    pass