import os
import subprocess
import threading
import time
from flask import Flask

app = Flask(__name__)
port = int(os.environ.get("PORT", 7860))

# Configuración de accesos y destinos
STREAM_URL = "https://cristianbracho904.blitz.cloud/hls/index.m3u8"
RTMP_DEST = "rtmp://ssh101.bozztv.com:1935/ssh101/canalczulia"

@app.route('/')
def index():
    return {
        "status": "ok",
        "enHorarioEmision": True,
        "message": "Retransmisor RTMP en modo copia (sin transcodificar) activo 24/7."
    }

# ==========================================
# 🎬 MOTOR DE TRANSMISIÓN EN MODO COPIA (24/7)
# ==========================================
def iniciar_retransmision():
    while True:
        print("🎬 [RTMP] Copiando señal directamente sin regenerar (0% esfuerzo de CPU)...")
        
        # Usamos '-c:v copy' y '-c:a copy' para reenviar el video idéntico al original
        args = [
            'ffmpeg',
            '-reconnect', '1',
            '-reconnect_streamed', '1',
            '-reconnect_delay_max', '5',
            '-fflags', '+genpts+igndts',
            '-i', STREAM_URL,
            '-c:v', 'copy',
            '-c:a', 'copy',
            '-f', 'flv',
            RTMP_DEST
        ]
        
        proceso = subprocess.Popen(args, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        
        ultimo_frame = time.time()
        
        def monitor_stderr():
            nonlocal ultimo_frame
            for line in proceso.stderr:
                if "frame=" in line or "size=" in line:
                    ultimo_frame = time.time()
        
        monitor_thread = threading.Thread(target=monitor_stderr, daemon=True)
        monitor_thread.start()
        
        # Watchdog: Si pasan más de 15 segundos sin actividad, reinicia el proceso
        while proceso.poll() is None:
            if time.time() - ultimo_frame > 15:
                print("⚠️ [Watchdog] La señal se congeló. Reiniciando proceso...")
                proceso.kill()
                break
            time.sleep(2)
            
        proceso.wait()
        print("⚠️ [RTMP] Proceso cerrado. Reintentando en 3 segundos...")
        time.sleep(3)

if __name__ == '__main__':
    hilo_streaming = threading.Thread(target=iniciar_retransmision, daemon=True)
    hilo_streaming.start()
    
    app.run(host='0.0.0.0', port=port)
 
