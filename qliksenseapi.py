import configparser, os, ssl, websocket, json
from datetime import datetime, date

class Configuracion():
    def __init__(self, pPath='./static', pFile='configuraciones.cfg'):
        self.config = configparser.ConfigParser()
        self.config.read_file(open(f'{pPath}/{pFile}', encoding='utf-8'))

    def get_url(self):
        protocolo   = self.config['qliksense']['protocolo']
        proxy       = self.config['qliksense']['proxy']
        puerto      = self.config['qliksense']['puerto']
        return f'{protocolo}://{proxy}:{puerto}'

    def get_path_certificado(self, pCertPath='./static/certs/'):
        path        = self.config['qliksense']['certificados']
        if not path:
            path = pCertPath
        return path

    def get_autenticacion(self, pDominio=None, pUsuario=None):
        dominio = pDominio if pDominio else self.config['qliksense']['dominio']
        usuario = pUsuario if pUsuario else self.config['qliksense']['usuario']
        return {'dominio': dominio, 'usuario': usuario}

    def get_informacion(self, pSeccion=None, pCampo=None, pDefault=None):
        info = None
        if pSeccion and pCampo:
            info = self.config[pSeccion][pCampo]
        else:
            info = pDefault
        return info

class ValidaArchivos():
    def __init__(self, pPath=None):
        self.path = pPath if pPath else os.getcwd()

    def lista_archivos(self, pPath=None):
        archivos = []
        path = pPath if pPath else self.path

        for elemento in os.listdir(path):
            elem_path = os.path.join(path, elemento)
            if os.path.isfile(elem_path):
                if not elem_path.endswith('.docx'):
                    archivos.append(elem_path)
            else:
                self.lista_archivos(elem_path)
        return archivos

    def genera_folder(self, pPath=None, *args):
        path = pPath if pPath else self.path
        for arg in args:
            path = os.path.join(path, arg)
            if not os.path.exists(path):
                os.mkdir(path)
        return path

    def renombrar_folder(self, pNombreAnterior, pNombreNuevo, pPath=None):
        path = pPath if pPath else self.path
        os.rename(os.path.join(path, pNombreAnterior), os.path.join(path, pNombreNuevo))

    def valida_antiguedad_dias(self, pArchivo, pDias = 1, pOperacion=">", pDefault=False):
        if os.path.exists(pArchivo):
            ahora       = datetime.now()
            ti_m        = os.path.getmtime(pArchivo)
            m_ti        = datetime.fromtimestamp(ti_m)
            diferencia  = ahora - m_ti
            if pOperacion == ">" and diferencia.days > pDias:
                return True
            elif pOperacion == "<" and diferencia.days < pDias:
                return True
            elif pOperacion == ">=" and diferencia.days >= pDias:
                return True
            elif pOperacion == "<=" and diferencia.days <= pDias:
                return True
            elif pOperacion == "==" and diferencia.days == pDias:
                return True
            else:
                return False
        return pDefault

    def del_archivos(self, pDias=1000):
        archivos        = []

        for archivo in self.lista_archivos():
            if self.valida_antiguedad(archivo, pDias, pOperacion=">"):
                archivos.append([archivo, m_ti, diferencia.days])
                os.remove(archivo)
        return archivos

class QSWebSockets():
    def __init__(self, debug=False, pPath=None, cert_path='./certs/', user_directory=None, user_id=None, hard_delete=False):
        conf                = Configuracion()
        self.archivo        = ValidaArchivos(pPath)
        ssl.match_hostname  = lambda cert, hostname: True
        websocket.enableTrace(debug)
        self.debug          = debug
        
        # Directorios
        certpath            = conf.get_path_certificado(cert_path)
        pathbasedir         = conf.get_informacion('qliksense', 'carpeta_base')
        datadir             = conf.get_informacion('qliksense', 'carpeta_data')
        eliminadosdir       = conf.get_informacion('qliksense', 'carpeta_eliminados')
        diaseliminacion     = conf.get_informacion('qliksense', 'dias_para_eliminar')
        logs_dir            = self.archivo.genera_folder(pathbasedir, 'logs', f'{date.today()}')
        self.base_data      = self.archivo.genera_folder(pathbasedir, datadir)
        self.log_file       = open(os.path.join(logs_dir, 'log.txt'), 'a')
        
        # Parametros de Concexión
        self.url            = conf.get_url()+'/app/'
        self.certs          = ({
                            "ca_certs": os.path.join(certpath, 'root.pem'), #conf.get_path_certificado(cert_path) + "root.pem", 
                            "certfile": os.path.join(certpath, 'client.pem'), #conf.get_path_certificado(cert_path) + "client.pem", 
                            "keyfile":  os.path.join(certpath, 'client_key.pem'), #conf.get_path_certificado(cert_path) + "client_key.pem", 
                            "cert_reqs": ssl.CERT_REQUIRED, 
                            "server_side": False
                        })
        self.credenciales   = conf.get_autenticacion(user_directory, user_id)
        # Conexiones
        self.ws             = self.new_connection()    
        
    def __del__(self):
        self.log_file.close()
        self.ws.close()
        
    def new_connection(self, ticket=None):
        url = f"{self.url}"
        url += f"{ticket}/" if ticket else ""
        conexion  = websocket.create_connection(url, sslopt=self.certs, header={
            "X-Qlik-User": f"UserDirectory={self.credenciales['dominio']}; UserId={self.credenciales['usuario']}"})
        print(conexion.recv() , ticket) # New session
        return conexion

    def define_request(self, handle=-1, method=None, **kwargs):
        if self.debug:
            print({ "handle": handle, "method": method, "params": kwargs, })
        return json.dumps({
            "handle": handle,
            "method": method,
            "params": kwargs,
        })

    def mensaje_log(self, mensaje, tabs=0, salto_linea=1):
        self.log_file.write('\t'*tabs + f'{datetime.now()} :: {mensaje}' + '\n'*salto_linea) 

    def get_all_streams(self, dir_trabajo='--- Trabajo ---'):
        streams_json_path = os.path.join(self.base_data, 'Streams.json')
        self.mensaje_log('INICIA EXTRACCIÓN DE STREAMS')
        self.mensaje_log('Crea o valida directorios para los stream', tabs=1)
        self.ws.send(self.define_request(method='GetStreamList'))
        data    = json.loads(self.ws.recv())
        data['result']['qStreamList'].append({"qName": dir_trabajo, "qId": '00000000000000000000000000000000'})
        # extraigo el original y el nuevo para validar las actualizaciones
        # y actualizar el nombre de las carpetas (no eliminar y volver a crearlas)
        streams_json = json.loads(json.dumps(data['result']['qStreamList']))
        try:
            streams_json_ini = json.load(open(streams_json_path))
        except Exception as e:
            streams_json_ini = []
        
        for stream_nuevo in streams_json:
            idx = next((index for (index, d) in enumerate(streams_json_ini) if d["qId"] == stream_nuevo['qId']), None)
            if not idx is None and idx >= 0:
                stream_ant = streams_json_ini.pop(idx)
                if stream_ant['qName'] != stream_nuevo['qName']:
                    self.mensaje_log(f'Stream (cambio de nombre): {stream_ant["qName"]} >> {stream_nuevo["qName"]} ({stream_nuevo["qId"]})', tabs=1)
                    self.archivo.renombrar_folder(stream_ant['qName'], stream_nuevo['qName'], self.base_data)
                
        with open(streams_json_path, 'w') as streams_json_file:
            streams_json_file.write(json.dumps(data['result']['qStreamList'], indent=4))
            
            for stream in data['result']['qStreamList']:
                self.mensaje_log(f'Stream: {stream["qName"]} ({stream["qId"]})', tabs=1)
                self.archivo.genera_folder(self.base_data, stream['qName'])
            
        self.mensaje_log('FINALIZA EXTRACCIÓN DE STREAMS', salto_linea=2)
        return streams_json

    def dict_value(self, pObjeto, pDefault=None, *args):
        if len(args) > 1:
            return self.dict_value(pObjeto, pDefault, args[1:])
        resultado = pObjeto.get(args[0])
        if resultado:
            return resultado
        return pDefault

    def get_model_file_name(self, pStreamName, pModelo, pModeloId, dir_trabajo='--- Trabajo ---'):
        stream_name = pStreamName['name'] if pStreamName else dir_trabajo
        return os.path.join(self.base_data, f'{stream_name}', f"{pModelo} - ({pModeloId})")

    def get_all_models(self, dir_trabajo='--- Trabajo ---'):
        modelos_dict = []
        self.mensaje_log('INICIA EXTRACCIÓN DE MODELOS')
        self.ws.send(self.define_request(method='GetDocList'))
        data                = json.loads(self.ws.recv())
        # extraigo el original y el nuevo para validar las actualizaciones
        # y actualizar el nombre de los archivos (para evitar dejar huerfanos algunos archivos)
        modelos_json        = json.loads(json.dumps(data['result']['qDocList']))
        
        for modelo in modelos_json:
            qId             = self.dict_value(modelo, None, 'qDocId')
            stream_file     = self.dict_value(modelo, dir_trabajo, 'qMeta','stream','name')
            modelo_file     = os.path.join(self.base_data, stream_file, f'{modelo["qDocName"]} ({qId})')
            modelos_dict.append({
                'id':       qId,
                'nombre':   modelo["qDocName"],
                'stream_id':   modelo['qMeta']['stream']['id'] if modelo['qMeta']['stream'] else '00000000000000000000000000000000',
            })
            
            try:
                if self.archivo.valida_antiguedad_dias(f"{modelo_file}.txt", pDias=1, pOperacion=">", pDefault=True):
                    self.mensaje_log(f'Conexión al modelo {modelo["qDocName"]} ({qId})', tabs=1)
                    ws_modelo       = self.new_connection(qId)
                    ws_modelo.send(self.define_request(handle=-1, method='OpenDoc', qDocName= f"{qId}", qNoData= False))
                    modelo_qReturn  = json.loads(ws_modelo.recv()) # respuesta OpenDoc
                    if modelo_qReturn['result']:
                        self.mensaje_log('Extracción load script', tabs=2)
                        ws_modelo.send(self.define_request(handle=modelo_qReturn['result']['qReturn']['qHandle'], method='GetScript'))
                        modelo_respuesta= json.loads(ws_modelo.recv()) # respuesta GetScript
                        with open(f"{modelo_file}.txt", 'w', encoding='utf-8') as file:
                                file.write(modelo_respuesta['result']['qScript'].replace('\r', ''))
                else:
                    self.mensaje_log(f'Existe el archivo script: {modelo["qDocName"]} ({qId})', tabs=1)
                
                if self.archivo.valida_antiguedad_dias(f"{modelo_file}.json", pDias = 1, pOperacion=">", pDefault=True):
                    self.mensaje_log('Extracción de campos', tabs=2)
                    ws_modelo.send(self.define_request(handle=modelo_qReturn['result']['qReturn']['qHandle'], method='CreateSessionObject', 
                        qProp= { 'qInfo': {'qType': 'FieldList' } , 'qFieldListDef': { 'qShowSrcTables': True } }) )
                    sessionobj_qReturn = json.loads(ws_modelo.recv())['result']['qReturn']
                    ws_modelo.send(self.define_request(handle=sessionobj_qReturn['qHandle'], method='GetLayout'))
                    sessionojb_respuesta = json.loads(ws_modelo.recv())
                    modelo['qFields'] = sessionojb_respuesta['result']['qLayout']['qFieldList']
                    with open(f"{modelo_file}.json", 'w', encoding='utf-8') as file:
                        file.write(json.dumps(modelo, indent=4))
                else:
                    self.mensaje_log(f'Existe el archivo json: {modelo["qDocName"]} ({qId})', tabs=1)

                    
            except Exception as e:
                self.mensaje_log(f'ERRROR: {modelo_file}', tabs=2)
                raise e

        self.mensaje_log('FINALIZA EXTRACCIÓN DE MODELOS')
        return modelos_dict
        
        