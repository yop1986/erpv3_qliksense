import uuid

from django.db import models
from django.db.models.constraints import UniqueConstraint
from django.utils.translation import gettext as _
from django.urls import reverse_lazy


class TipoLicencia(models.Model):
    '''
        Tipo de licencias contratadas para hacer uso de la herramienta.
    '''
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    descripcion = models.CharField(_('Descripción'), max_length = 120, unique = True)
    cantidad    = models.PositiveSmallIntegerField(verbose_name = _('Cantidad'))

    def __str__(self):
        return self.descripcion

    def licencias_asignadas(self):
        return Area_TipoLicencia.objects.filter(tipo=self, vigente=True).count()

    def licencias_no_asignadas(self):
        return self.cantidad - self.licencias_asignadas()

    def url_detail(self):
        return reverse_lazy('qliksense:detail_licencia', kwargs={'pk': self.id})

    def url_update(self):
        return reverse_lazy('qliksense:update_licencia', kwargs={'pk': self.id})

    def url_delete(self):
        return reverse_lazy('qliksense:delete_licencia', kwargs={'pk': self.id})


class Area(models.Model):
    '''
        Area responsable del uso de la licencia
    '''
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre      = models.CharField(_('Nombre'), max_length = 120, unique = True)

    def __str__(self):
        return f'{self.nombre}'

    def url_detail(self):
        return reverse_lazy('qliksense:detail_area', kwargs={'pk': self.id})

    def url_update(self):
        return reverse_lazy('qliksense:update_area', kwargs={'pk': self.id})

    def url_delete(self):
        return reverse_lazy('qliksense:delete_area', kwargs={'pk': self.id})


class Area_TipoLicencia(models.Model):
    '''
        Asignacion de tipos de licencia por área, para determinar los costos
        por su adquisición.
    '''
    cantidad    = models.PositiveSmallIntegerField(verbose_name=_('Cantidad'))
    vigente     = models.BooleanField(_('Estado'), default=True)

    tipo        = models.ForeignKey(TipoLicencia, on_delete = models.RESTRICT)
    area        = models.ForeignKey(Area, on_delete = models.RESTRICT)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['tipo', 'area'], name='unq_atl_area_tipo')
        ]

    def __str__(self):
        return f'{self.area.nombre} ({self.licencias_disponibles()})'

    def licencias_usadas(self):
        return Usuario.objects.filter(area_tipo=self, vigente=True).count()

    def licencias_disponibles(self):
        return self.cantidad - self.licencias_usadas()

    def url_parent_detail(self):
        return self.area.url_detail()
    


class Usuario (models.Model):
    '''
        Usuario con licencia asignada
    '''
    TIPOS = [
        ('USR', 'USR'),
        ('OUT', 'OUT'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tipo        = models.CharField(_('Tipo de usuario'), choices=TIPOS, max_length=3)
    # def_tipo_display()
    codigo      = models.PositiveIntegerField(verbose_name=_('Código'))
    nombre      = models.CharField(_('Nombre'), max_length=120)
    extension   = models.CharField(_('Exstensión'), max_length=6)
    correo      = models.CharField(_('Correo'), max_length=120)
    vigente     = models.BooleanField(_('Estado'), default=True)

    area_tipo   = models.ForeignKey(Area_TipoLicencia, on_delete=models.RESTRICT)

    def __str__(self):
        return f'{self.nombre} ({self.tipo}{str(self.codigo).zfill(6)})'

    