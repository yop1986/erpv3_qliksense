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

    path('qlik/', include('qliksense.urls')),

#### Configuracion

Es necesario realiar la configuración para permitir la conexión a traves del Engine de Qlik
a esta aplicación y sincronizar la información.

    [qliksense]
    # Se utiliza para realizar la conexión a los streams y modelos de qliksense
    qs_webproxy     = 

    # Se utiliz para generar las urls de conexion a los web_socket
    protocolo       = wss
    proxy           = 
    puerto          = 
    certificados    =

    #Usuario para autenticarse en la api de qlik
    dominio         = 
    usuario         = 

    #Carpeta para guardar los script
    CarpetaLScript  = D:\Backup\Qlik\QlikJson
    CarpetaElimiando= Eliminados
    DiasEliminacion = 91

##### Certificados

Es necesario colocar en la carpeta static en la raiz del proyecto la carpeta certs/ que contiene los certificados
que permitirán la conexion segura del usuario a la API de Qlik Sense. (Estos certificados se generan desde el QMC)

#### Comandos adicionales de Django

    (venv) ERPv3> python manage.py check
    (venv) ERPv3> python manage.py migrate qliksense
