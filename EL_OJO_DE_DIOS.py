import paho.mqtt.client as mqtt
import sys
from xmlrpc.client import ServerProxy
import json
import time
import datetime
import os

# Configuración del pasillo
PASILLO_IP = "192.168.0.212"
PASILLO_PORT = 8081
BROKER_IP = "192.168.0.100"
BROKER_PORT = 1883
TOPIC_BASE = "axis/B8A44FA146EE/event/#"
TOPIC_TEST = "axis/B8A44FA146EE/test1"
SIMULACION_ACTIVA = True  # Cambia a False para desactivar la simulación

# Conexión con el pasillo
try:
    pasillo = ServerProxy(f'http://{PASILLO_IP}:{PASILLO_PORT}', allow_none=True, use_builtin_types=True)
    modoAEA = pasillo.SetModeAEA("E")
    estado_pasillo_actual = "00000000"  # Estado inicial del pasillo
except Exception as e:
    print("❌ No se pudo conectar con el pasillo. Verifique la conexión.")
    sys.exit()

# Estados del pasillo
PASILLO_ESTADOS = {
    "00000000": "✅ Pasillo OK",
    "01000100": "🚨 Pasillo en Emergencia",
    "00001000": "⛔ Pasillo Bloqueado",
    "00000010": "🔧 Pasillo en Mantenimiento"
}

def registrar_evento(mensaje):
    """Registra eventos en un archivo de log."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {mensaje}"
    print(log_message)
    with open("eventos_pasillo.log", "a") as log_file:
        log_file.write(log_message + "\n")

def procesar_mensaje(payload):
    """Procesa un mensaje MQTT recibido o simulado."""
    try:
        data = json.loads(payload)
        human_count = int(data["message"]["data"].get("human", 0))
        scenarios = data["message"]["data"].get("scenarioType", [])
        if isinstance(scenarios, str):
            scenarios = [scenarios]  # Convertir a lista si solo hay un escenario

        print(f"👥 Personas detectadas: {human_count} | 🎯 Escenarios: {', '.join(scenarios)}")
        
        # Bloqueo por múltiples personas
        if human_count >= 2:
            pasillo.SetModeAEA("L")
            print("🚨 ¡Alerta! Pasillo bloqueado por seguridad: Se detectó más de una persona.")
            registrar_evento("Bloqueo: Más de una persona detectada en el pasillo.")
            time.sleep(2)
            pasillo.SetModeAEA("E")
            print("🟢 Pasillo desbloqueado automáticamente después de 2 segundos.")
            registrar_evento("Pasillo desbloqueado automáticamente.")
        
        # Bloqueo por cruce de línea
        elif "LineCrossing" in scenarios:
            pasillo.SetModeAEA("L")
            print("🚨 ¡Alerta! Pasillo bloqueado por pasajero en sentido contrario.")
            registrar_evento("Bloqueo: Pasajero detectado en dirección contraria.")
            time.sleep(2)
            pasillo.SetModeAEA("E")
            print("🟢 Pasillo desbloqueado automáticamente después de 2 segundos.")
            registrar_evento("Pasillo desbloqueado automáticamente.")
    
    except json.JSONDecodeError:
        print("❌ Error: Mensaje no es JSON válido.")
    except Exception as e:
        print("❌ Error inesperado en procesamiento de mensaje.", str(e))

def on_message(client, userdata, message):
    """Maneja los mensajes MQTT recibidos."""
    procesar_mensaje(message.payload.decode('utf-8'))

def simular_mensaje():
    """Simula un mensaje de detección de dos personas en el área."""
    mensaje_simulado = {
        "message": {
            "data": {
                "human": "2",
                "scenarioType": "OccupancyInArea"
            }
        }
    }
    procesar_mensaje(json.dumps(mensaje_simulado))

# Configuración del cliente MQTT
client = mqtt.Client()
client.on_message = on_message
    
try:
    client.connect(BROKER_IP, BROKER_PORT)
    client.subscribe([(TOPIC_BASE, 0), (TOPIC_TEST, 0)])
    print("✅ Suscripción exitosa. Esperando mensajes...")
    
    # Simulación de mensaje después de iniciar si está activada
    if SIMULACION_ACTIVA:
        time.sleep(3)
        print("🔄 Simulando detección de dos personas...")
        simular_mensaje()
    
    client.loop_forever()
except Exception as e:
    print("❌ Error en la conexión MQTT.", str(e))
