import paho.mqtt.client as mqtt
import json

# Datos del broker
BROKER_IP = "192.168.0.100"
BROKER_PORT = 1883

# Temas a los que quieres suscribirte
TOPIC_BASE = "axis/B8A44FA146EE/event/#"  # Captura todos los eventos
TOPIC_TEST = "axis/B8A44FA146EE/test1"    # Para mensajes de prueba

# Función para procesar los mensajes
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
            print(f"🎯 Tipo de Escenario: {scenario_type}")

            # Identificar el tipo de escenario y realizar acciones
            if scenario_type == "ObjectInArea":
                print("🔵 ¡Objeto detectado en el área!")
            elif scenario_type == "LineCrossing":
                print("🟢 ¡Cruce de línea detectado!")
            elif scenario_type == "OccupancyInArea":
                print("🟠 ¡Más de una persona en el área!")
            else:
                print(f"⚠️ Escenario desconocido: {scenario_type}")

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
