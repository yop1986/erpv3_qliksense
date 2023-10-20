# ERPv3 - QlikSense

## Desarrollo

### Configuración del Ambiente

Esta aplicacion depende del [Modulo de usuarios](https://github.com/yop1986/erpv3_usuarios) 
por lo que es necesario instalar este y sus dependencias previamente.

Desde la consola de Git se procede a clonar este repositorio, en la raiz del 
proyecto.

    $ git clone https://github.com/yop1986/erpv3_qliksense.git qliksense

Es necesario instalar las dependencias detalladas en el archivo 
_dependencias.txt_

    (venv) ERPv3>pip install -r usuarios/dependencias.txt

*dependencias creadas por medio del comando __pip freeze > dependencias.txt__*

#### Settings

Es necesario modificar el archivo **settings.py** del proyecto general con la
siguiente informacion:

    INSTALLED_APPS = [
        ...
        'crispy_forms',
        'crispy_bootstrap5',
        'simple_history',
        
        'usuarios',
        'qliksense',
    ]

    MIDDLEWARE = [
        ...
        'simple_history.middleware.HistoryRequestMiddleware',
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
    (venv) ERPv3> python manage.py makemigrations
    (venv) ERPv3> python manage.py migrate


## Producción

### Configuración del Ambiente


Cuando se instale en producción se debe generar otra clave y Debug = False

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure--yy^#vtem@522nqsw4)69-ddtc_^xn&p#sl74$&jkw1^g9azy8'
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True