import configparser, os, ssl, websocket, json, shutil
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
        '''
            Lista todos los archivos en el Path indicado
        '''
        archivos = []
        path = pPath if pPath else self.path

        for elemento in os.listdir(path):
            elem_path = os.path.join(path, elemento)
            if os.path.isfile(elem_path):
                if not elem_path.endswith('.docx'):
                    archivos.append(elem_path)
            else:
                archivos = archivos + self.lista_archivos(elem_path)
        return archivos

    def genera_folder(self, pPath=None, *args):
        '''
            Genera folders de acuerdo con los parametros en el Path indicado
        '''
        path = pPath if pPath else self.path
        for arg in args:
            path = os.path.join(path, arg)
            if not os.path.exists(path):
                os.mkdir(path)
        return path

    def renombrar_folder(self, pNombreAnterior, pNombreNuevo, pPath=None):
        '''
            Renombra el nombre del directorio (ultimo en el árbol) dentro del path
        '''
        path = pPath if pPath else self.path
        os.rename(os.path.join(path, pNombreAnterior), os.path.join(path, pNombreNuevo))

    def valida_antiguedad_dias(self, pArchivo, pDias=1, pOperacion=">", pDefault=False):
        '''
            Valida la antiguedad de los archivos enviados, contra las condiciones evaluando a verdadero
            cuando las mismas se cumplen.
        '''
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

    def mov_archivos(self, pArchivoOrigen, pPathDestino, pDias=1000):
        '''
            Mueve los archivos origen al destino si supera los días indicados. (utiliza
            el mismo nombre de archivo que el original - solo cambia de ubicacion -)
        '''
        archivos        = []
        for archivo in self.lista_archivos(pArchivoOrigen):
            if self.valida_antiguedad_dias(archivo, pDias):
                # archivos.append([archivo, m_ti, diferencia.days])
                # os.remove(archivo)
                destino =  os.path.join(pPathDestino, os.path.basename(archivo))
                shutil.move(archivo, destino)
                archivos.append(f'{archivo} --> {destino}')
        return archivos

class QSWebSockets():
    def __init__(self, debug=False, pPath=None, cert_path='./certs/', user_directory=None, user_id=None, hard_delete=False):
        websocket.enableTrace(debug)
        ssl.match_hostname  = lambda cert, hostname: True
        conf                = Configuracion()

        self.debug          = conf.get_informacion('qliksense', 'qs_socket_debug')
        self.archivo        = ValidaArchivos(pPath)
        
        # Parametros de conexión
        self.url            = conf.get_url()+'/app/'
        certpath            = conf.get_path_certificado(cert_path)
        self.certs          = ({
                            "ca_certs": os.path.join(certpath, 'root.pem'), 
                            "certfile": os.path.join(certpath, 'client.pem'), 
                            "keyfile":  os.path.join(certpath, 'client_key.pem'), 
                            "cert_reqs": ssl.CERT_REQUIRED, 
                            "server_side": False
                        })
        self.credenciales   = conf.get_autenticacion(user_directory, user_id)
        
        # Streams default
        self.working_stream = conf.get_informacion('qliksense', 'working_stream')
        self.working_stream_id = conf.get_informacion('qliksense', 'working_stream_id', '00000000000000000000000000000000')

        # Directorios
        pathbasedir         = conf.get_informacion('qliksense', 'carpeta_base')
        datadir             = conf.get_informacion('qliksense', 'carpeta_data')
        eliminadosdir       = conf.get_informacion('qliksense', 'carpeta_eliminados')
        logs_dir            = self.archivo.genera_folder(pathbasedir, 'logs', f'{date.today()}')
        self.base_data      = self.archivo.genera_folder(pathbasedir, datadir)
        self.dir_eliminados = self.archivo.genera_folder(pathbasedir, eliminadosdir, f'{date.today()}')
        self.log_file       = open(os.path.join(logs_dir, 'log.txt'), 'a')

        try:
            self.diaseliminacion= int(conf.get_informacion('qliksense', 'dias_para_eliminar'))
        except Exception as e:
            self.diaseliminacion= 1
            
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

    def dict_value(self, pObjeto, pDefault=None, *args):
        if len(args) > 1:
            return self.dict_value(pObjeto.get(args[0]), pDefault, *args[1:])
        resultado = pObjeto.get(args[0]) if pObjeto else None

        if resultado:
            return resultado
        return pDefault

    def mensaje_log(self, mensaje, tabs=0, salto_linea=1):
        self.log_file.write('\t'*tabs + f'{datetime.now()} :: {mensaje}' + '\n'*salto_linea) 

    def get_all_streams(self):
        streams_json_path = os.path.join(self.base_data, 'Streams.json')
        self.mensaje_log('INICIA EXTRACCIÓN DE STREAMS')
        self.mensaje_log('Crea o valida directorios para los stream', tabs=1)
        self.ws.send(self.define_request(method='GetStreamList'))
        data    = self.dict_value(json.loads(self.ws.recv()), None, 'result', 'qStreamList')
        # Se agrega informacion del directorio de trabajo
        data.append({"qName": self.working_stream, "qId": self.working_stream_id})
        # extraigo el original y el nuevo para validar las actualizaciones
        # y actualizar el nombre de las carpetas (no eliminar y volver a crearlas)
        try:
            streams_json_ini = json.load(open(streams_json_path))
        except Exception as e:
            streams_json_ini = []
        
        for stream_nuevo in data:
            idx = next((index for (index, d) in enumerate(streams_json_ini) if d["qId"] == stream_nuevo['qId']), None)
            if not idx is None and idx >= 0:
                stream_ant = streams_json_ini.pop(idx)
                if stream_ant and stream_ant['qName'] != stream_nuevo['qName']:
                    self.mensaje_log(f'Stream (cambio de nombre): {stream_ant["qName"]} >> {stream_nuevo["qName"]} ({stream_nuevo["qId"]})', tabs=1)
                    self.archivo.renombrar_folder(stream_ant['qName'], stream_nuevo['qName'], self.base_data)
                
        with open(streams_json_path, 'w') as streams_json_file:
            streams_json_file.write(json.dumps(data, indent=4))
            
            for stream in data:
                self.mensaje_log(f'Stream: {stream["qName"]} ({stream["qId"]})', tabs=1)
                self.archivo.genera_folder(self.base_data, stream['qName'])
            
        self.mensaje_log('FINALIZA EXTRACCIÓN DE STREAMS', salto_linea=2)
        return data

    def get_model_file_name(self, pStreamName, pModelo, pModeloId):
        stream_name = pStreamName['name'] if pStreamName else self.working_stream
        return os.path.join(self.base_data, f'{stream_name}', f"{pModelo} - ({pModeloId})")

    def get_all_models(self):
        modelos_dict = []
        self.mensaje_log('INICIA EXTRACCIÓN DE MODELOS')
        self.ws.send(self.define_request(method='GetDocList'))
        data                = self.dict_value(json.loads(self.ws.recv()), None, 'result', 'qDocList')

        for modelo in data:
            qId             = self.dict_value(modelo, None, 'qDocId')
            qName           = self.dict_value(modelo, None, "qDocName")
            stream_file     = self.dict_value(modelo, self.working_stream, 'qMeta','stream','name')
            modelo_file     = os.path.join(self.base_data, stream_file, f'{qName} ({qId})')
            modelos_dict.append({
                'id':       qId,
                'nombre':   qName,
                'stream_id': self.dict_value(modelo, self.working_stream_id, 'qMeta','stream','id'),
            })
            self.mensaje_log(f'--> : {qName} :: {qId}', tabs=1)

            ws_modelo       = self.new_connection(qId)
            ws_modelo.send(self.define_request(handle=-1, method='OpenDoc', qDocName= f"{qId}", qNoData= False))
            respuesta       = json.loads(ws_modelo.recv())
            modelo_qResult  = self.dict_value(respuesta, None, 'result') # respuesta OpenDoc
            
            if not modelo_qResult:
                self.mensaje_log(f'No se pudo establecer la conexion: {modelo_file} :: {respuesta}')
                break

            self.mensaje_log(f'Conexión al modelo {qName} ({qId})', tabs=1)
            modelo_qHandle  = self.dict_value(modelo_qResult, None, 'qReturn', 'qHandle')

            if self.archivo.valida_antiguedad_dias(f"{modelo_file}.txt", pDias=1, pOperacion=">", pDefault=True):
                self.mensaje_log('Extracción load script', tabs=2)
                ws_modelo.send(self.define_request(handle=modelo_qHandle, method='GetScript'))
                respuesta   = json.loads(ws_modelo.recv()) # respuesta GetScript
                with open(f"{modelo_file}.txt", 'w', encoding='utf-8') as file:
                    file.write(self.dict_value(respuesta, None, 'result', 'qScript').replace('\r', ''))
            else:
                self.mensaje_log(f'Modelo ya recargado (Script): {qName} ({qId}) -- {modelo_qHandle} --', tabs=1)
            
            if self.archivo.valida_antiguedad_dias(f"{modelo_file}.json", pDias = 1, pOperacion=">", pDefault=True):
                self.mensaje_log('Extracción de campos', tabs=2)
                ws_modelo.send(self.define_request(handle=modelo_qHandle, method='CreateSessionObject', 
                    qProp= { 'qInfo': {'qType': 'FieldList' } , 'qFieldListDef': { 'qShowSrcTables': True } }) )
                respuesta   = json.loads(ws_modelo.recv()) # respuesta CreateSessionObject
                obj_qHandle = self.dict_value(respuesta, None, 'result', 'qReturn', 'qHandle')
                ws_modelo.send(self.define_request(handle=obj_qHandle, method='GetLayout'))
                respuesta   = json.loads(ws_modelo.recv()) # respuesta GetLayout
                modelo['qFields'] = self.dict_value(respuesta, None, 'result', 'qLayout', 'qFieldList')
                with open(f"{modelo_file}.json", 'w', encoding='utf-8') as file:
                    file.write(json.dumps(modelo, indent=4))
            else:
                self.mensaje_log(f'Modelo ya recargado (Json): {qName} ({qId}) -- {modelo_qHandle} --', tabs=1)

            #ws_modelo.send(self.define_request(handle=-1, method='OpenDoc', qDocName= f"{qId}", qNoData= False))
            ws_modelo.close()

        self.mensaje_log('FINALIZA EXTRACCIÓN DE MODELOS', salto_linea=2)
        self.mensaje_log('Depuración de modelos inexistentes (no actualizados)')
        for archivo in self.archivo.mov_archivos(self.base_data, self.dir_eliminados, self.diaseliminacion):
            self.mensaje_log(archivo, tabs=1)
        self.mensaje_log('Finaliza depuración de modelos inexistentes (no actualizados)')
        return modelos_dict