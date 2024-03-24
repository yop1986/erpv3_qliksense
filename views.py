import os, json

from django.apps import apps
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views.generic.base import TemplateView

from simple_history.utils import bulk_create_with_history

from usuarios.personal_views import (PersonalContextMixin, PersonalCreateView, 
    PersonalUpdateView, PersonalListView, PersonalDetailView, PersonalDeleteView, 
    PersonalFormView, Configuracion)

from .models import (TipoLicencia, Area, Area_TipoLicencia, Usuario,
    Stream, Modelo)
from .forms import Area_TipoLicencia_ModelForm, UsuarioCreate_ModelForm, UsuarioUpdate_ModelForm
from .qliksenseapi import QSWebSockets # Configuracion as ApiConfig, ValidaArchivos

gConfiguracion = Configuracion()

DISPLAYS = {
    'forms': {
        'submit': _('Guardar'),
        'cancel': _('Cancelar'),
    },
    'delete_form': {
        'confirmacion': _('¿Esta seguro de eliminar el elemento indicado?'),
        'submit': _('Eliminar'),
        'cancel': _('Cancelar'),
    },
    'disable_form': {
        'confirmacion': _('¿Esta seguro de inhabilitar el elemento indicado?'),
        'submit': _('Inhabilitar'),
        'cancel': _('Cancelar'),
    },
    'opciones': {
        'detail': _('Ver'),
        'detail_img': 'qs_detail.png',
        'update': _('Editar'),
        'update_img': 'qs_update.png',
        'delete': _('Eliminar'),
        'delete_img': 'qs_delete.png',
    },
    'tabla_vacia': _('No hay elementos para mostrar'),
}

class QlikContextMixin(PersonalContextMixin):
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['general']['menu_app'] = apps.get_app_config(__package__).name +'_menu.html'
        return context 

### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### 
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### 
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### 

class IndexTemplateView(TemplateView, QlikContextMixin):
    template_name = 'template/index.html'

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


class LicenciasListView(PersonalListView, QlikContextMixin):
    permission_required = 'qliksense.view_tipolicencia'
    template_name = 'template/list.html'
    model = TipoLicencia
    ordering = ['descripcion']
    paginate_by = 10
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
        'campos_extra': [
            {
                'nombre':   _('Disponibles'), #display
                # valor, constante o funcion 
                'funcion': 'licencias_no_asignadas',  
            },
        ],
        'opciones': DISPLAYS['opciones'],
        'create' :{
            'display':  _('Nuevo'),
            'url':      TipoLicencia.url_create(),
        },
        'mensaje': {
            'vacio': DISPLAYS['tabla_vacia'],
        },
    }

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['permisos'] = {
            'create': self.request.user.has_perm('qliksense.add_tipolicencia'),
            'update': self.request.user.has_perm('qliksense.change_tipolicencia'),
            'delete': self.request.user.has_perm('qliksense.delete_tipolicencia'),
        }
        return context

class LicenciasCreateView(PersonalCreateView, QlikContextMixin):
    permission_required = 'qliksense.add_tipolicencia'
    template_name = 'template/forms.html'
    model = TipoLicencia
    fields = ['descripcion', 'cantidad']
    #form_class = 
    success_url = reverse_lazy('qliksense:list_licencia')
    extra_context = {
        'title': _('Nuevo tipo de licencia'),
        'opciones': DISPLAYS['forms'],
    }

class LicenciasDetailView(PersonalDetailView, QlikContextMixin):
    permission_required = 'qliksense.view_tipolicencia'
    template_name = 'template/detail.html'
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
        context['permisos'] = {
            'create': self.request.user.has_perm('qliksense.add_tipolicencia'),
            'update': self.request.user.has_perm('qliksense.change_tipolicencia'),
            'delete': self.request.user.has_perm('qliksense.delete_tipolicencia'),
        }
        context['campos_adicionales'] = [ 
            {'display': _('Licencias asignadas'), 'valor': self.object.licencias_asignadas()},
            {'display': _('Licencias pendientes'), 'valor': self.object.licencias_no_asignadas()},
        ]
        if self.request.user.has_perm('qliksense.add_area_tipolicencia'):
            context['forms'] = [
                {
                    'modal':    'area_tipolicencia', 
                    'action':   reverse_lazy('qliksense:create_areatipo')+f'?next='+self.object.url_detail(),
                    'display':  _('Asignación de licencias'),
                    'link_img': 'qs_areatipolicencia.png',
                    'form':     Area_TipoLicencia_ModelForm('tipo', instance=Area_TipoLicencia(tipo=self.object)),
                    'opciones': DISPLAYS['forms'],
                },
            ]
        if self.request.user.has_perm('qliksense.view_area'):   
            context['tables'] = [
                {
                    'title':        _('Areas'),
                    'enumerar':     1,
                    'object_list':  Area_TipoLicencia.objects.filter(tipo=self.object).order_by('area__nombre'),
                    'campos':       ['area', 'cantidad'],
                    'opciones':     _('Opciones'),
                    'campos_extra': [
                        {
                            'nombre':   _('Asignadas'), #display
                            # valor, constante o funcion 
                            'funcion': 'licencias_asignadas',  
                        },
                        {
                            'nombre':   _('Disponibles'), #display
                            # valor, constante o funcion 
                            'funcion': 'licencias_disponibles',  
                        },
                    ],
                    'permisos': {
                        'update':   self.request.user.has_perm('qliksense.change_area_tipolicencia'),
                        'delete':   self.request.user.has_perm('qliksense.delete_area_tipolicencia'),
                    },
                    'next':         self.object.url_detail(),
                },
            ]
        return context

class LicenciasUpdateView(PersonalUpdateView, QlikContextMixin):
    permission_required = 'qliksense.change_tipolicencia'
    template_name = 'template/forms.html'
    model = TipoLicencia
    fields = ['descripcion', 'cantidad']
    extra_context = {
        'title': _('Modificar tipo de licencia'),
        'opciones': DISPLAYS['forms'],
    }

    def get_success_url(self):
        return self.object.url_detail()

class LicenciasDeleteView(PersonalDeleteView, QlikContextMixin):
    permission_required = 'qliksense.delete_tipolicencia'
    template_name = 'template/delete_confirmation.html'
    model = TipoLicencia
    success_url = reverse_lazy('qliksense:list_licencia')
    extra_context = {
        'title': _('Eliminar tipo de licencia'),
        'opciones': DISPLAYS['delete_form'],
    }


class AreaListView(PersonalListView, QlikContextMixin):
    permission_required = 'qliksense.view_area'
    template_name = 'template/list.html'
    model = Area
    ordering = ['nombre']
    paginate_by = 10
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
        'create' :{
            'display':  _('Nueva'),
            'url':      Area.url_create(),
        },
        'mensaje': {
            'vacio': DISPLAYS['tabla_vacia'],
        },
    }

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['permisos'] = {
            'create': self.request.user.has_perm('qliksense.add_area'),
            'update': self.request.user.has_perm('qliksense.change_area'),
            'delete': self.request.user.has_perm('qliksense.delete_area'),
        }
        return context

class AreaCreateView(PersonalCreateView, QlikContextMixin):
    permission_required = 'qliksense.add_area'
    template_name = 'template/forms.html'
    model = Area
    fields = ['nombre']
    #form_class = 
    #success_url = 
    extra_context = {
        'title': _('Area/Gerencia'),
        'opciones': DISPLAYS['forms'],
    }

    def get_success_url(self):
        return self.object.url_detail()

class AreaDetailView(PersonalDetailView, QlikContextMixin):
    permission_required = 'qliksense.view_area'
    template_name = 'template/detail.html'
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
        context['permisos'] = {
            'create': self.request.user.has_perm('qliksense.add_area'),
            'update': self.request.user.has_perm('qliksense.change_area'),
            'delete': self.request.user.has_perm('qliksense.delete_area'),
        }
        if self.request.user.has_perm('qliksense.add_area_tipolicencia'):
            context['forms'] = [
                {
                    'modal':    'area_tipolicencia', 
                    'action':   reverse_lazy('qliksense:create_areatipo')+f'?next='+self.object.url_detail(),
                    'display':  _('Asignación de licencias'),
                    'link_img': 'qs_areatipolicencia.png',
                    'form':     Area_TipoLicencia_ModelForm('area', instance=Area_TipoLicencia(area=self.object)),
                    'opciones': DISPLAYS['forms'],
                },
            ]
        if self.request.user.has_perm('qliksense.view_tipolicencia'):
            context['tables'] = [
                {
                    'title':        _('Licencias'),
                    'enumerar':     1,
                    'object_list':  Area_TipoLicencia.objects.filter(area=self.object).order_by('tipo__descripcion'),
                    'campos':       ['tipo', 'cantidad'],
                    'campos_extra': [
                        {
                            'nombre':   _('Asignadas'), #display
                            # valor, constante o funcion 
                            'funcion': 'licencias_asignadas',  
                        },
                        {
                            'nombre':   _('Disponibles'), #display
                            # valor, constante o funcion 
                            'funcion': 'licencias_disponibles',  
                        },
                    ],
                    'permisos': {
                        'update':   self.request.user.has_perm('qliksense.change_area_tipolicencia'),
                        'delete':   self.request.user.has_perm('qliksense.delete_area_tipolicencia'),
                    },
                    'opciones':     _('Opciones'),
                    #Si tiene next, redirecciona a esa pagina
                    'next':         self.object.url_detail(),
                },
            ]
        return context

class AreaUpdateView(PersonalUpdateView, QlikContextMixin):
    permission_required = 'qliksense.change_area'
    template_name = 'template/forms.html'
    model = Area
    fields = ['nombre']
    #form_class = 
    #success_url = 
    extra_context = {
        'title': _('Modificar área / gerencia'),
        'opciones': DISPLAYS['forms'],
    }

    def get_success_url(self):
        return self.object.url_detail()

class AreaDeleteView(PersonalDeleteView, QlikContextMixin):
    permission_required = 'qliksense.delete_area'
    template_name = 'template/delete_confirmation.html'
    model = Area
    success_url = reverse_lazy('qliksense:list_area')
    extra_context = {
        'title': _('Eliminar area / gerencia'),
        'opciones': DISPLAYS['delete_form'],
    }


class Area_TipoLicenciaFormView(PersonalFormView, QlikContextMixin):
    permission_required = 'qliksense.add_area_tipolicencia'
    template_name = 'template/forms.html'
    model = Area_TipoLicencia
    form_class = Area_TipoLicencia_ModelForm
    success_url = reverse_lazy('qliksense:list_licencia')
    success_message = 'Asignación exitosa'
    extra_context = {
        'title': _('Asignación de licencias'),
        'opciones': DISPLAYS['forms'],
    }

    def get_form_kwargs(self, **kwargs):
        kwargs = super().get_form_kwargs()
        redirect = self.request.GET.get('next')
        if redirect:
            self.success_url = redirect
        return kwargs

    def form_valid(self, form, *args, **kwargs):
        data = form.cleaned_data
        area_tipo = Area_TipoLicencia(**data)
        area_tipo.save()
        return super().form_valid(form)

class Area_TipoLicenciaUpdateView(PersonalUpdateView, QlikContextMixin):
    permission_required = 'qliksense.change_area_tipolicencia'
    template_name = 'template/forms.html'
    model = Area_TipoLicencia
    fields = ['cantidad']
    #form_class = 
    #success_url = 
    success_message = 'Re-asignación exitosa'
    extra_context = {
        'title': _('Modificar Asiganción'),
        'opciones': DISPLAYS['forms'],
    }

    def get_form_kwargs(self, **kwargs):
        kwargs = super().get_form_kwargs()
        redirect = self.request.GET.get('next')
        if redirect:
            self.success_url = redirect
        return kwargs

class Area_TipoLicenciaDeleteView(PersonalDeleteView, QlikContextMixin):
    permission_required = 'qliksense.delete_area_tipolicencia'
    template_name = 'template/delete_confirmation.html'
    model = Area_TipoLicencia
    #success_url =
    extra_context = {
        'title': _('Eliminar asignación'),
        'opciones': DISPLAYS['delete_form'],
    }

    def get_form_kwargs(self, **kwargs):
        kwargs = super().get_form_kwargs()
        redirect = self.request.GET.get('next')
        if redirect:
            self.success_url = redirect
        return kwargs


class UsuarioListView(PersonalListView, QlikContextMixin):
    permission_required = 'qliksense.view_usuario'
    template_name = 'template/list.html'
    model = Usuario
    ordering = ['-vigente', 'area_tipo__area', 'area_tipo__tipo']
    paginate_by = 10
    extra_context = {
        'title': _('Usuarios'),
        'campos': {
            #-1: no enumera
            # 0: inicia numeración en 0
            # 1: inicia numeración en 1
            'enumerar': 1,
            # Si hay valor se muestra opciones por linea, de lo contrario no se muestran
            'opciones': _('Opciones'),
            # Lista de campos que se deben mostrar en la tabla
            'lista': [
                'area_tipo', 'nombre', 'extension', 'correo', 
            ],
        },
        'opciones': DISPLAYS['opciones'],
        'create' :{
            'display':  _('Nuevo'),
            'url':      Usuario.url_create(),
        },
        'mensaje': {
            'vacio': DISPLAYS['tabla_vacia'],
        },
    }

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['permisos'] = {
            'create': self.request.user.has_perm('qliksense.add_usuario'),
            'update': self.request.user.has_perm('qliksense.change_usuario'),
            'delete': self.request.user.has_perm('qliksense.delete_usuario'),
        }
        return context

class UsuarioCreateView(PersonalCreateView, QlikContextMixin):
    permission_required = 'qliksense.add_usuario'
    template_name = 'template/forms.html'
    model = Usuario
    #fields = ['tipo', 'codigo', 'nombre', 'extension', 'correo', 'area_tipo']
    form_class = UsuarioCreate_ModelForm
    success_url = reverse_lazy('qliksense:list_usuario')
    extra_context = {
        'title': _('Nuevo usuario'),
        'opciones': DISPLAYS['forms'],
    }

class UsuarioUpdateView(PersonalUpdateView, QlikContextMixin):
    permission_required = 'qliksense.change_usuario'
    template_name = 'template/forms.html'
    model = Usuario
    #fields = ['nombre']
    form_class = UsuarioUpdate_ModelForm
    success_url = reverse_lazy('qliksense:list_usuario')
    extra_context = {
        'title': _('Modificar área / gerencia'),
        'opciones': DISPLAYS['forms'],
    }

class UsuarioDeleteView(PersonalDeleteView, QlikContextMixin):
    permission_required = 'qliksense.delete_usuario'
    template_name = 'template/delete_confirmation.html'
    model = Usuario
    success_url = reverse_lazy('qliksense:list_usuario')
    extra_context = {
        'title': _('Eliminar asignación a usuario'),
        'opciones': DISPLAYS['delete_form'],
    }

### 

class StreamListView(PersonalListView, QlikContextMixin):
    permission_required = 'qliksense.view_stream'
    template_name = 'template/list.html'
    model = Stream
    ordering = ['nombre']
    paginate_by = 10
    extra_context = {
        'title': _('Streams'),
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
        'botones_extra':[
            {
                'display':  _('Recargar'),
                'url':      reverse_lazy('qliksense:refresh_all_data'),
                'img':      'qs_refresh.png',
            
            },
        ],
        'mensaje': {
            'vacio': DISPLAYS['tabla_vacia'],
        },
    }

class StreamDetailView(PersonalDetailView, QlikContextMixin):
    permission_required = 'qliksense.view_stream'
    template_name = 'template/detail.html'
    model = Stream
    extra_context = {
        'title': _('Stream'),
        'campos': {
            #'opciones': _('Opciones'),
            #'lista': [
            #    'nombre' 
            #],
        },
        'opciones': DISPLAYS['opciones'],
    }

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        if self.request.user.has_perm('qliksense.view_modelo'): 
            context['tables'] = [
                {
                    'title':        _('Modelos'),
                    'enumerar':     1,
                    'object_list':  Modelo.objects.filter(stream=self.object).order_by('nombre'),
                    'campos':       ['nombre'],
                    'permisos': {
                        'detail':   self.request.user.has_perm('qliksense.view_modelo'),
                    },
                    'opciones':     _('Opciones'),
                },
            ]

        return context

def refresh_all(request):
    if request.user.is_authenticated:
        qs_ws = QSWebSockets()
        stream_refresh(request, qs_ws)
        model_refresh(request, qs_ws)
        return redirect(reverse_lazy('qliksense:list_stream'))
    return redirect(reverse_lazy('usuarios:login') + '?next=' + reverse_lazy('qliksense:refresh_all_data'))

def stream_refresh(request, qs_ws):
    '''
        Obtiene los Streams correspondientes, actualiza sus nombres y los crea en caso de ser nuevos.
        Elimina los streams que ya no existen en Qlik.
    '''
    streams = Stream.objects.all()
    array_insert = []

    for element in qs_ws.get_all_streams():
        stream = streams.filter(id = element['qId'])
        streams = streams.exclude(id = element['qId'])
        if stream:
            if not stream.filter(nombre = element['qName']):
                stream[0].nombre = element['qName']
                stream[0]._history_user = request.user
                stream[0].save()
        else:
            stream = Stream(id = element['qId'], nombre=element['qName'])
            stream._history_user = request.user
            array_insert.append(stream)

    streams.delete()
    bulk_create_with_history(array_insert, Stream, batch_size=500)

def model_refresh(request, qs_ws):
    '''
        Obtiene los Modelos correspondientes, crea y actualiza el modelo de acuerdo con el id generado desde Qlik.
        Elimina modelos que ya no existen en Qlik.
    '''
    modelos = Modelo.objects.all()
    array_insert=[]

    for element in qs_ws.get_all_models():
        modelo = modelos.filter(id = element['id'])
        modelos = modelos.exclude(id = element['id'])
        if modelo:
            if not modelo.filter(nombre = element['nombre']) or not modelo.filter(stream_id = element['stream_id']):
                modelo[0].nombre = element['nombre']
                modelo[0].stream_id = element['stream_id']
                modelo[0]._history_user = request.user
                modelo[0].save()
        else:
            modelo = Modelo(id = element['id'], nombre = element['nombre'], stream_id = element['stream_id'])
            modelo._history_user = request.user
            array_insert.append(modelo)
    
    for m in modelos:
        m._history_user = request.user
    modelos.delete()
    
    bulk_create_with_history(array_insert, Modelo, batch_size=500)


class ModelDetailView(PersonalDetailView, QlikContextMixin):
    permission_required = 'qliksense.view_modelo'
    template_name = 'template/detail.html'
    model = Modelo
    extra_context = {
        'title': _('Modelo'),
        'campos': {
            #'opciones': _('Opciones'),
            #'lista': [
            #    'nombre' 
            #],
        },
        'opciones': DISPLAYS['opciones'],
    }

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        context['manual_tables'] = [
            {
                'title':        _('Campos'),
                'enumerar':     1,
                'object_list':  self.campo_valores(self.object),
                'campos':       ['Nombre', 'Tipo'],
                'opciones':     _('Opciones'),
            },
        ]

        return context

    def campo_valores(self, pObj):
        if self.request.user.is_authenticated:
            file = os.path.join(gConfiguracion.get_value('qliksense', 'carpeta_base'), gConfiguracion.get_value('qliksense', 'carpeta_data'), pObj.stream.nombre, f"{pObj.nombre} ({pObj.id}).json")
            datos = []
            for element in json.load(open(file)).get('qFields').get('qItems'):
                datos.append([element['qName'], self.campo_tipo(element['qTags'])])
            return datos
        return None

    def campo_tipo(self, valores):
        if '$date' in valores:
            return _('Fecha/Hora')
        elif '$integer' in valores:
            return _('Entero')
        elif '$numeric' in valores:
            return _('Decimal')
        elif '$text' in valores:
            return _('Texto')
        else:
            return '-'