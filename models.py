import uuid

from django.conf import settings
from django.db import models
from django.db.models.constraints import UniqueConstraint
from django.utils.translation import gettext as _
from django.urls import reverse_lazy

from simple_history.models import HistoricalRecords


class TipoLicencia(models.Model):
    '''
        Tipo de licencias contratadas para hacer uso de la herramienta.
    '''
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    descripcion = models.CharField(_('Descripción'), max_length = 120, unique = True)
    cantidad    = models.PositiveSmallIntegerField(verbose_name = _('Cantidad'))

    history     = HistoricalRecords(user_model=settings.AUTH_USER_MODEL)

    def __str__(self):
        return self.descripcion

    def licencias_asignadas(self):
        cantidad = Area_TipoLicencia.objects.filter(tipo=self, vigente=True)\
            .aggregate(models.Sum('cantidad'))['cantidad__sum']
        return cantidad if cantidad else 0

    def licencias_no_asignadas(self):
            return self.cantidad - self.licencias_asignadas()

    def url_create():
        return reverse_lazy('qliksense:create_licencia')

    def url_detail(self):
        return reverse_lazy('qliksense:detail_licencia', kwargs={'pk': self.id})

    def url_update(self):
        return reverse_lazy('qliksense:update_licencia', kwargs={'pk': self.id})

    def url_delete(self):
        if Area_TipoLicencia.objects.filter(tipo = self.id).count()>0:
            return None
        return reverse_lazy('qliksense:delete_licencia', kwargs={'pk': self.id})


class Area(models.Model):
    '''
        Area responsable del uso de la licencia
    '''
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre      = models.CharField(_('Nombre'), max_length = 120, unique = True)

    history     = HistoricalRecords(user_model=settings.AUTH_USER_MODEL)

    def __str__(self):
        return f'{self.nombre}'

    def url_create():
        return reverse_lazy('qliksense:create_area')

    def url_detail(self):
        return reverse_lazy('qliksense:detail_area', kwargs={'pk': self.id})

    def url_update(self):
        return reverse_lazy('qliksense:update_area', kwargs={'pk': self.id})

    def url_delete(self):
        if Area_TipoLicencia.objects.filter(area=self.id):
            return None
        return reverse_lazy('qliksense:delete_area', kwargs={'pk': self.id})


class Area_TipoLicencia(models.Model):
    '''
        Asignacion de tipos de licencia por área, para determinar los costos
        por su adquisición.
    '''
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cantidad    = models.PositiveSmallIntegerField(verbose_name=_('Cantidad'))
    vigente     = models.BooleanField(_('Estado'), default=True)

    tipo        = models.ForeignKey(TipoLicencia, on_delete = models.RESTRICT)
    area        = models.ForeignKey(Area, on_delete = models.RESTRICT)

    history     = HistoricalRecords(user_model=settings.AUTH_USER_MODEL)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['tipo', 'area'], name='unq_atl_area_tipo')
        ]

    def __str__(self):
        return f'{self.area.nombre} / {self.tipo.descripcion} ({self.licencias_disponibles()})'

    def licencias_asignadas(self):
        return Usuario.objects.filter(vigente=True, area_tipo=self).count()

    def licencias_disponibles(self):
        return self.cantidad - self.licencias_asignadas()

    def url_update(self):
        return reverse_lazy('qliksense:update_areatipo', kwargs={'pk': self.id})

    def url_delete(self):
        if Usuario.objects.filter(area_tipo = self.id).count()>0:
            return None
        return reverse_lazy('qliksense:delete_areatipo', kwargs={'pk': self.id})


class Usuario (models.Model):
    '''
        Usuario con licencia asignada
    '''
    TIPOS = [
        ('USR', 'USR'),
        ('OUT', 'OUT'),
    ]
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tipo        = models.CharField(_('Tipo de usuario'), choices=TIPOS, max_length=3)
    # def_tipo_display()
    codigo      = models.PositiveIntegerField(verbose_name=_('Código'))
    nombre      = models.CharField(_('Nombre'), max_length=120)
    extension   = models.CharField(_('Exstensión'), max_length=6, blank=True, null=True)
    correo      = models.CharField(_('Correo'), max_length=120, blank=True, null=True)
    vigente     = models.BooleanField(_('Estado'), default=True)
    creacion    = models.DateField(_('Ingreso'), auto_now_add=True)
    actualizacion = models.DateField(_('Actualización'), auto_now=True)

    area_tipo   = models.ForeignKey(Area_TipoLicencia, verbose_name=_('Area/Tipo'), on_delete=models.RESTRICT)

    history     = HistoricalRecords(excluded_fields=['creacion', 'actualizacion'], user_model=settings.AUTH_USER_MODEL)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['tipo', 'codigo'], name='unq_usr_tipo_codigo'),
        ]

    def __str__(self):
        return f'{self.nombre} ({self.get_usuario_dominio()})'

    def get_usuario_dominio(self):
        return f'{self.tipo}{str(self.codigo).zfill(6)}'

    def url_create():
        return reverse_lazy('qliksense:create_usuario')

    def url_update(self):
        return reverse_lazy('qliksense:update_usuario', kwargs={'pk': self.id})

    def url_delete(self):
        if Usuario.objects.filter(area_tipo = self.id).count()>0:
            return None
        return reverse_lazy('qliksense:delete_usuario', kwargs={'pk': self.id})
