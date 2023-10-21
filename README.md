# ERPv3 - QlikSense

## Desarrollo

### Configuración del Ambiente

Esta aplicacion depende del [Modulo de usuarios](https://github.com/yop1986/erpv3_usuarios) 
por lo que es necesario instalar este y sus dependencias previamente.

Desde la consola de Git se procede a clonar este repositorio, en la raiz del 
proyecto.

    $ git clone https://github.com/yop1986/erpv3_qliksense.git qliksense

#### Settings

Es necesario modificar el archivo **settings.py** del proyecto general con la
siguiente informacion:

    INSTALLED_APPS = [
        ...
        'qliksense',
    ]

    INFORMACION_APLICACIONES = {
        'qliksense': {
            'nombre':       'Qlik Sense',
            'descripcion':  _('Aplicación de controles administrativos para Qlik Sense.'),
            'url':          reverse_lazy('qliksense:index'),
            'imagen':       'qs_qliksense.png',
        },
    }

#### Urls

Posterior a esta configuracion es necesario agregar las urls al proyecto base __< Base >/urls.py__

    path('qlik', include('qliksense.urls')),

#### Comandos adicionales de Django

    (venv) ERPv3> python manage.py check
    (venv) ERPv3> python manage.py makemigrations qliksense
    (venv) ERPv3> python manage.py migrate qliksense
