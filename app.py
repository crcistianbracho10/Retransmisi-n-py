import os
import subprocess
import threading
import time
import streamlit as st

# Configuración de la interfaz de Streamlit
st.set_page_config(page_title="Retransmisor RTMP", layout="centered")

st.title("🚀 Retransmisor RTMP Activo (24/7)")
st.write("El motor de retransmisión se está ejecutando en segundo plano hacia BozzTV en modo copia.")

# Configuración de accesos y destinos
STREAM_URL = "https://cristianbracho904.blitz.cloud/hls/index.m3u8"
RTMP_DEST = "rtmp://ssh101.bozztv.com:1935/ssh101/canalczulia"

# Estado en la interfaz
if "estado" not in st.session_state:
    st.session_state.estado = "Iniciando conexión..."

status_placeholder = st.empty()

# ==========================================
# 🎬 MOTOR DE TRANSMISIÓN EN SEGUNDO PLANO
# ==========================================
def iniciar_retransmision():
    while True:
        try:
            print("🎬 [RTMP] Copiando señal directamente sin transcodificar...")
            st.session_state.estado = "Transmitiendo en vivo (Modo Copia)"
            
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
            
            # Watchdog: Si pasan más de 15 segundos sin frames, reinicia el proceso
            while proceso.poll() is None:
                if time.time() - ultimo_frame > 15:
                    print("⚠️ [Watchdog] La señal se congeló. Reiniciando proceso...")
                    st.session_state.estado = "Reiniciando por señal congelada..."
                    proceso.kill()
                    break
                time.sleep(2)
                
            proceso.wait()
        except Exception as e:
            print(f"❌ Error: {e}")
            st.session_state.estado = f"Error: {e}"
            
        print("⚠️ [RTMP] Proceso cerrado. Reintentando en 3 segundos...")
        time.sleep(3)

# Iniciar el hilo de retransmisión una sola vez al cargar la app
if "hilo_iniciado" not in st.session_state:
    st.session_state.hilo_iniciado = True
    hilo_streaming = threading.Thread(target=iniciar_retransmision, daemon=True)
    hilo_streaming.start()

# Mostrar estado en pantalla
status_placeholder.info(f"**Estado actual:** {st.session_state.estado}")

st.markdown("---")
st.write("💡 *Nota: Mantén esta pestaña de Streamlit abierta o asegúrate de que tu app no entre en modo 'Sleep' por inactividad si tu cuenta es gratuita.*")
