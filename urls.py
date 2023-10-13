from django.urls import path, include

from . import views

app_name = 'qliksense'

urlpatterns = [
    path('', views.IndexTemplateView.as_view(), name='index'),

    path('licencia/', views.LicenciasListView.as_view(), name='list_licencia'),
    path('licencia/nueva/', views.LicenciasCreateView.as_view(), name='create_licencia'),
    path('licencia/ver/<uuid:pk>', views.LicenciasDetailView.as_view(), name='detail_licencia'),
    path('licencia/actualizar/<uuid:pk>', views.LicenciasUpdateView.as_view(), name='update_licencia'),
    path('licencia/eliminar/<uuid:pk>', views.LicenciasDeleteView.as_view(), name='delete_licencia'),

    path('area/', views.AreaListView.as_view(), name='list_area'),
    path('area/nueva/', views.AreaCreateView.as_view(), name='create_area'),
    path('area/ver/<uuid:pk>', views.AreaDetailView.as_view(), name='detail_area'),
    path('area/actualizar/<uuid:pk>', views.AreaUpdateView.as_view(), name='update_area'),
    path('area/eliminar/<uuid:pk>', views.AreaDeleteView.as_view(), name='delete_area'),

    path('area_tipolicencia/nueva/', views.Area_TipoLicenciaFormView.as_view(), name='create_areatipo'),
    path('area_tipolicencia/actualizar/<uuid:pk>', views.Area_TipoLicenciaUpdateView.as_view(), name='update_areatipo'),
    path('area_tipolicencia/eliminar/<uuid:pk>', views.Area_TipoLicenciaDeleteView.as_view(), name='delete_areatipo'),

    path('usuario/', views.UsuarioListView.as_view(), name='list_usuario'),
    path('usuario/nuevo/', views.UsuarioCreateView.as_view(), name='create_usuario'),
    path('usuario/actualizar/<uuid:pk>', views.UsuarioUpdateView.as_view(), name='update_usuario'),
    path('usuario/eliminar/<uuid:pk>', views.UsuarioDeleteView.as_view(), name='delete_usuario'),

]


    




    
    