from django.urls import path, include

from . import views

app_name = 'qliksense'

urlpatterns = [
    path('', views.IndexTemplateView.as_view(), name='index'),

    path('licencias/', views.LicenciasListView.as_view(), name='list_licencia'),
    path('licencias/nueva/', views.LicenciasCreateView.as_view(), name='create_licencia'),
    path('licencias/actualizar/<uuid:pk>', views.LicenciasUpdateView.as_view(), name='update_licencias'),
    path('licencias/ver/<uuid:pk>', views.LicenciasDetailView.as_view(), name='detail_licencias'),
    path('licencias/eliminar/<uuid:pk>', views.LicenciasDeleteView.as_view(), name='delete_licencias'),
]


    




    
    