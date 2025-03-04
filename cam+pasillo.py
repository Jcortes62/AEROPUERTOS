import paho.mqtt.client as mqtt
import sys
from xmlrpc.client import ServerProxy
import json
import time


#Comunicacion con el pasillo
s = ServerProxy('http://192.168.0.212:8081', allow_none=True, use_builtin_types=True)
modoAEA = s.SetModeAEA("E")
print(type(modoAEA))
inicio_pasillo = int(modoAEA[0])

estado=s.GetStatus(0)
est = estado[0]

print(type(est))
print(est)

if est == "00000000":
    print("Pasillo ok")
elif est == "01000100":
    print("Pasillo En Emergencia")
elif est == "00001000":
    print("pasillo bloquedo")
elif est == "00000010":
    print("Pasillo En Mantenimiento")
else:
    print("error")
        

if inicio_pasillo == 1 and est == "00000000" :
    print("pasillo modo E")
    print("Iniciando camara...")
    time.sleep(5)# Pausa de 5 segundos
    # Datos del broker
    BROKER_IP = "192.168.0.100"
    BROKER_PORT = 1883
    # Temas a los que quieres suscribirte
    TOPIC_BASE = "axis/B8A44FA146EE/event/#"  # Captura todos los eventos
    TOPIC_TEST = "axis/B8A44FA146EE/test1"    # Para mensajes de prueba
    def on_message(client, userdata, message):
        try:
            payload = message.payload.decode('utf-8')
            print(f"\n📬 Mensaje recibido en '{message.topic}': {payload}")

            # Intentar interpretar el mensaje como JSON
            data = json.loads(payload)

            # Verificar si es un mensaje de conexión
            if "description" in data and data["description"] == "Connected":
                print("✅ ¡Cámara conectada exitosamente!")

            # Verificar si el mensaje contiene la información esperada
            if "scenarioType" in data["message"]["data"]:
                scenario_type = data["message"]["data"]["scenarioType"]
                print(type(scenario_type))
                print(f"🎯 Tipo de Escenario: {scenario_type}")
                
                
                # Extraer el valor de 'human' si está presente
                human_count = int(data["message"]["data"].get("human", "0"))
                print(f"👤 Cantidad de personas: {human_count}")
                
                if human_count >= 2:
                    modoAEA = s.SetModeAEA("L")
                    print("pasillo bloqueado por por pasajeros")
                    time.sleep(2)# Pausa de 2 segundos
                elif scenario_type == "LineCrossing":
                    modoAEA = s.SetModeAEA("L")
                    print("pasillo bloqueado por por pasajeros")
                    time.sleep(2)# Pausa de 2 segundos
                elif human_count == 1 or 0:
                    modoAEA = s.SetModeAEA("E")

        except json.JSONDecodeError:
            print("❌ Error: El mensaje no es JSON válido.")
        except Exception as e:
            print(f"❌ Error inesperado: {e}")

    # Configurar el cliente MQTT
    client = mqtt.Client()
    client.on_message = on_message

    # Conectarse al broker
    print(f"🔌 Conectando a {BROKER_IP}:{BROKER_PORT}...")
    client.connect(BROKER_IP, BROKER_PORT)

    # Suscribirse a los temas
    client.subscribe(TOPIC_BASE)
    client.subscribe(TOPIC_TEST)
    print("✅ Suscripción exitosa. Esperando mensajes...")

    # Mantener el cliente funcionando
    client.loop_forever()
    print("Continuando después de la pausa")
    
else:
    print("no fue posible iniciar")
    sys.exit()


    




