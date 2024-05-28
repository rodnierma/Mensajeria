from flask import Flask, request,jsonify,render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

app = Flask(__name__)

#Configuración de la Base de Datos SQLITE
#Modelo de la Tabla LOG
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///metapython.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Log(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    fecha_y_hora=db.Column(db.DateTime, default=datetime.utcnow)
    texto=db.Column(db.TEXT)

#Crear la Tabla 
with app.app_context():
    db.create_all()
    
    prueba1 = Log(texto='Mensaje de Prueba 1')
    prueba2 = Log(texto='Mensaje de Prueba 2')

    db.session.add(prueba1)
    db.session.add(prueba2)
    db.session.commit()

#Funcion para ordenar los registros por fecha y hora
def ordenar_por_fecha_y_hora(registros):
    return sorted(registros, key=lambda x: x.fecha_y_hora, reverse=True)

@app.route('/')
def index():
    #Obtener todos los registros de la Base de Datos
    registros=Log.query.all()
    registros_ordenados=ordenar_por_fecha_y_hora(registros)
    return render_template('index.html',registros=registros_ordenados)

mensajes_log = []

#Funcion para agregar mensajes y guardar en la base de datos
def agregar_mensajes_log(texto):
    mensajes_log.append(texto)

    #Guardar el mensaje en la base de datos
    nuevo_registro = Log(texto=texto)
    db.session.add(nuevo_registro)
    db.session.commit()

#TOKEN De Verificación para la configuración
TOKEN_ANDERCODE = "ANDERCODE"

@app.route('/webhook',methods=['GET','POST'])
def webhook():
    if request.method == 'GET':
        challenge = verificar_token(request)
        return challenge
    elif request.method == 'POST':
        response = recibir_mensajes(request)
        return response

def verificar_token(req):
    token=req.args.get('hub.verify_token')
    challenge = req.args.get('hub.challenge')

    if challenge and token == TOKEN_ANDERCODE:
        return challenge
    else:
        return jsonify({'error':'Token Invalido'}),401
    

def recibir_mensajes(req):
    try:
        req = request.get_json()
        entry =req['entry'][0]
        changes = entry['changes'][0]
        value = changes['value']
        objeto_mensaje = value['messages']

        if objeto_mensaje:
            messages = objeto_mensaje[0]

            if "type" in messages:
                tipo = messages["type"]
                #Guardar Log en la BD
                agregar_mensajes_log(json.dumps(messages))        

                if tipo == "interactive":
                    tipo_interactivo = messages["interactive"]["type"]

                    if tipo_interactivo == "button_reply":
                        text = messages["interactive"]["button_reply"]["id"]
                        numero = messages["from"]

                        enviar_mensajes_whatsapp(text,numero)
                    
                    elif tipo_interactivo == "list_reply":
                        text = messages["interactive"]["list_reply"]["id"]
                        numero = messages["from"]

                        enviar_mensajes_whatsapp(text,numero)

                if "text" in messages:
                    text = messages["text"]["body"]
                    numero = messages["from"]

                    enviar_mensajes_whatsapp(text,numero)

                    agregar_mensajes_log(json.dumps(text))
                    agregar_mensajes_log(json.dumps(numero))

        return jsonify({'message':'EVENT_RECEIVED'})
    except Exception as e:
        return jsonify({'message':'EVENT_RECEIVED'})
    
def enviar_mensajes_whatsapp(texto,number):
    texto = texto.lower()    

if __name__=='__main__':
    app.run(host='0.0.0.0',port=80,debug=True)
