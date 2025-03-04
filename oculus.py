import sys
import json
import time
import datetime
import os
import logging
import requests
import paho.mqtt.client as mqtt
import cv2
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QFont, QPalette, QLinearGradient, QColor, QBrush, QPixmap, QImage
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from xmlrpc.client import ServerProxy

# Configurar logs
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logging.info("Iniciando aplicación")

# Comunicación con el pasillo
try:
    s = ServerProxy('http://192.168.0.212:8081', allow_none=True, use_builtin_types=True)
    modoAEA = s.SetModeAEA("E")
    inicio_pasillo = int(modoAEA[0])
    logging.info("Conexión con el pasillo establecida correctamente")
except Exception as e:
    logging.error(f"Error conectando con el pasillo: {e}")
    s = None
    inicio_pasillo = None

# Configuración de la cámara
CAMERA_URL = "rtsp://root:admin@192.168.0.90/axis-media/media.amp"

def obtener_estado_pasillo():
    if not s:
        return "Error de conexión con pasillo"
    try:
        estado = s.GetStatus(0)
        est = estado[0]
        pasillo_estados = {
            "00000000": "Pasillo ok",
            "01000100": "Pasillo en Emergencia",
            "00001000": "Pasillo bloqueado",
            "00000010": "Pasillo en Mantenimiento"
        }
        return pasillo_estados.get(est, "Error")
    except Exception as e:
        logging.error(f"Error obteniendo estado del pasillo: {e}")
        return "Error"

class VideoThread(QThread):
    frame_signal = pyqtSignal(QImage)
    error_signal = pyqtSignal(str)
    
    def run(self):
        logging.info("Iniciando hilo de captura de video")
        cap = cv2.VideoCapture(CAMERA_URL)
        if not cap.isOpened():
            logging.error("No se pudo abrir la cámara")
            self.error_signal.emit("Error: No se pudo abrir la cámara")
            return
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret or frame is None:
                logging.warning("No se pudo leer el frame de la cámara")
                self.error_signal.emit("Error: No se pudo leer el frame")
                time.sleep(0.1)
                continue
            
            try:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_frame.shape
                bytes_per_line = ch * w
                qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                self.frame_signal.emit(qt_image)
                logging.debug("✅ Frame enviado correctamente")
            except Exception as e:
                logging.error(f"Error procesando frame de video: {e}")
                self.error_signal.emit("Error procesando video")
                continue
            
            time.sleep(0.03)
        
        cap.release()
        logging.info("Hilo de captura de video finalizado")

class PasilloUI(QWidget):
    instancia = None

    def __init__(self):
        super().__init__()
        PasilloUI.instancia = self
        
        self.pasos = 0
        self.personas = 0
        self.fraudes = 0
        self.initUI()
        
        self.timer_estado = QTimer(self)
        self.timer_estado.timeout.connect(self.actualizar_estado_pasillo)
        self.timer_estado.start(2000)
        
        self.video_thread = VideoThread()
        self.video_thread.frame_signal.connect(self.actualizar_video)
        self.video_thread.error_signal.connect(self.mostrar_error_video)
        self.video_thread.start()
        logging.info("Interfaz gráfica iniciada")
        
    def initUI(self):
        self.setWindowTitle("Monitor de Pasillo")
        self.setFixedSize(600, 800)
        
        palette = QPalette()
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0.0, QColor(80, 80, 80))
        gradient.setColorAt(1.0, QColor(200, 200, 200))
        palette.setBrush(QPalette.Window, QBrush(gradient))
        self.setPalette(palette)
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        
        titulo = QLabel("Monitor de Pasillo")
        titulo.setFont(QFont("Arial", 14, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("color: white;")
        
        self.video_label = QLabel("Cargando video...")
        self.video_label.setFixedSize(500, 200)
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("background-color: black; color: white; border-radius: 10px;")
        
        indicadores_layout = QHBoxLayout()
        self.lbl_pasos = QLabel(f"Conteo de pasos\n{self.pasos}")
        self.lbl_personas = QLabel(f"Personas detectadas\n{self.personas}")
        self.lbl_fraudes = QLabel(f"Fraudes\n{self.fraudes}")
        
        for lbl in [self.lbl_pasos, self.lbl_personas, self.lbl_fraudes]:
            lbl.setFont(QFont("Arial", 16, QFont.Bold))
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("background-color: lightgray; border-radius: 10px; padding: 10px;")
            indicadores_layout.addWidget(lbl)
        
        self.estado_label = QLabel("Estado del pasillo: " + obtener_estado_pasillo())
        self.estado_label.setFont(QFont("Arial", 14))
        self.estado_label.setAlignment(Qt.AlignLeft)
        self.estado_label.setStyleSheet("background-color: darkgray; border-radius: 10px; padding: 10px;")
        
        main_layout.addWidget(titulo)
        main_layout.addWidget(self.video_label, alignment=Qt.AlignCenter)
        main_layout.addLayout(indicadores_layout)
        main_layout.addWidget(self.estado_label)
        
        self.setLayout(main_layout)

    def actualizar_video(self, image):
        if image.isNull():
            logging.error("⚠️ La imagen recibida es nula. No se actualizará el video.")
            return
        logging.debug("✅ Frame de video recibido correctamente")
        self.video_label.setPixmap(QPixmap.fromImage(image).scaled(self.video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
    
    def mostrar_error_video(self, mensaje):
        self.video_label.setText(mensaje)
    
    def actualizar_estado_pasillo(self):
        self.estado_label.setText("Estado del pasillo: " + obtener_estado_pasillo())

if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        ventana = PasilloUI()
        ventana.show()
        sys.exit(app.exec_())
    except Exception as e:
        logging.critical(f"Error crítico en la aplicación: {e}", exc_info=True)
