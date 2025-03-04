import paho.mqtt.client as mqtt

# Datos del broker (tu PC)
BROKER_IP = "192.168.0.100"  # Usa 'localhost' o la IP si es otra máquina
BROKER_PORT = 1883


# Temas a los que quieres suscribirte
TOPIC_1 = "axis/B8A44FA146EE/test1"
TOPIC_2 = "axis/B8A44FA146EE/event/#"  # Suscribe a todos los subtemas de "event"
TOPIC_3 = "axis/B8A44FA146EE/doblePasajero"

# Función que se ejecuta cuando recibes un mensaje
def on_message(client, userdata, message):
    print(f"\n📬 Mensaje recibido en '{message.topic}':")
    print(message.payload.decode("utf-8"))

    # Detectar si el usuario está en el área
    if "usuario dentro del area" in message.payload.decode("utf-8"):
        print("🚨 ¡Alerta! Usuario detectado en el área.")
        # Aquí puedes llamar una función para ejecutar una acción (por ejemplo, enviar una alerta o tomar una foto)

# Configurar el cliente MQTT
client = mqtt.Client()
client.on_message = on_message

# Conectarse al broker
print(f"🔌 Conectando a {BROKER_IP}:{BROKER_PORT}...")
client.connect(BROKER_IP, BROKER_PORT)

# Suscribirse a los temas
client.subscribe(TOPIC_1)
client.subscribe(TOPIC_2)
client.subscribe(TOPIC_3)
print("✅ Suscripción exitosa. Esperando mensajes...")

# Mantener el cliente funcionando
client.loop_forever()


