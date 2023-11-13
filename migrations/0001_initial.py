# Generated by Django 4.2.6 on 2023-11-10 16:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Area',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=120, unique=True, verbose_name='Nombre')),
            ],
        ),
        migrations.CreateModel(
            name='Area_TipoLicencia',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('cantidad', models.PositiveSmallIntegerField(verbose_name='Cantidad')),
                ('vigente', models.BooleanField(default=True, verbose_name='Estado')),
                ('area', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='qliksense.area')),
            ],
        ),
        migrations.CreateModel(
            name='Stream',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=120, unique=True, verbose_name='Nombre')),
            ],
        ),
        migrations.CreateModel(
            name='TipoLicencia',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('descripcion', models.CharField(max_length=120, unique=True, verbose_name='Descripción')),
                ('cantidad', models.PositiveSmallIntegerField(verbose_name='Cantidad')),
            ],
        ),
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('tipo', models.CharField(choices=[('USR', 'USR'), ('OUT', 'OUT')], max_length=3, verbose_name='Tipo de usuario')),
                ('codigo', models.PositiveIntegerField(verbose_name='Código')),
                ('nombre', models.CharField(max_length=120, verbose_name='Nombre')),
                ('extension', models.CharField(blank=True, max_length=6, null=True, verbose_name='Exstensión')),
                ('correo', models.CharField(blank=True, max_length=120, null=True, verbose_name='Correo')),
                ('vigente', models.BooleanField(default=True, verbose_name='Estado')),
                ('creacion', models.DateField(auto_now_add=True, verbose_name='Ingreso')),
                ('actualizacion', models.DateField(auto_now=True, verbose_name='Actualización')),
                ('area_tipo', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='qliksense.area_tipolicencia', verbose_name='Area/Tipo')),
            ],
        ),
        migrations.CreateModel(
            name='Modelo',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=90, verbose_name='Nombre')),
                ('descripcion', models.CharField(blank=True, max_length=210, verbose_name='Descripción')),
                ('stream', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='modelo_stream', to='qliksense.stream', verbose_name='Stream')),
            ],
        ),
        migrations.CreateModel(
            name='HistoricalUsuario',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False)),
                ('tipo', models.CharField(choices=[('USR', 'USR'), ('OUT', 'OUT')], max_length=3, verbose_name='Tipo de usuario')),
                ('codigo', models.PositiveIntegerField(verbose_name='Código')),
                ('nombre', models.CharField(max_length=120, verbose_name='Nombre')),
                ('extension', models.CharField(blank=True, max_length=6, null=True, verbose_name='Extensión')),
                ('correo', models.CharField(blank=True, max_length=120, null=True, verbose_name='Correo')),
                ('vigente', models.BooleanField(default=True, verbose_name='Estado')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('area_tipo', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='qliksense.area_tipolicencia', verbose_name='Area/Tipo')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical usuario',
                'verbose_name_plural': 'historical usuarios',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalTipoLicencia',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False)),
                ('descripcion', models.CharField(db_index=True, max_length=120, verbose_name='Descripción')),
                ('cantidad', models.PositiveSmallIntegerField(verbose_name='Cantidad')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical tipo licencia',
                'verbose_name_plural': 'historical tipo licencias',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalStream',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False)),
                ('nombre', models.CharField(db_index=True, max_length=120, verbose_name='Nombre')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical stream',
                'verbose_name_plural': 'historical streams',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalModelo',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False)),
                ('nombre', models.CharField(max_length=90, verbose_name='Nombre')),
                ('descripcion', models.CharField(blank=True, max_length=210, verbose_name='Descripción')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('stream', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='qliksense.stream', verbose_name='Stream')),
            ],
            options={
                'verbose_name': 'historical modelo',
                'verbose_name_plural': 'historical modelos',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalArea_TipoLicencia',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False)),
                ('cantidad', models.PositiveSmallIntegerField(verbose_name='Cantidad')),
                ('vigente', models.BooleanField(default=True, verbose_name='Estado')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('area', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='qliksense.area')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('tipo', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='qliksense.tipolicencia')),
            ],
            options={
                'verbose_name': 'historical area_ tipo licencia',
                'verbose_name_plural': 'historical area_ tipo licencias',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalArea',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False)),
                ('nombre', models.CharField(db_index=True, max_length=120, verbose_name='Nombre')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical area',
                'verbose_name_plural': 'historical areas',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.AddField(
            model_name='area_tipolicencia',
            name='tipo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='qliksense.tipolicencia'),
        ),
        migrations.AddConstraint(
            model_name='usuario',
            constraint=models.UniqueConstraint(fields=('tipo', 'codigo'), name='unq_usr_tipo_codigo'),
        ),
        migrations.AddConstraint(
            model_name='area_tipolicencia',
            constraint=models.UniqueConstraint(fields=('tipo', 'area'), name='unq_atl_area_tipo'),
        ),
    ]
