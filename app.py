
import streamlit as st
import subprocess
import shutil
import os
import time
import threading

st.set_page_config(
    page_title="Canal C del Zulia",
    page_icon="📺",
    layout="centered",
)

SOURCE = "https://lbgo.bozztv.com/ssh101/ssh101/"
DESTINATION = "rtmp://a.rtmp.youtube.com/live2/wr4f-kh3x-84ra-0gb8-861e"
LOG_FILE = "/tmp/canal_c_ffmpeg.log"


class Transmitter:
    def __init__(self):
        self.process = None
        self.lock = threading.Lock()
        self.status = "INICIANDO"
        self.last_error = ""
        self.log_file = None
        self.started = False

    def start(self):
        with self.lock:
            if self.started:
                return
            self.started = True

            ffmpeg = shutil.which("ffmpeg")
            if not ffmpeg:
                self.status = "ERROR: FFmpeg no instalado"
                self.last_error = "No se encontró FFmpeg en PATH."
                return

            try:
                self.log_file = open(LOG_FILE, "a", buffering=1)

                command = [
                    ffmpeg,
                    "-hide_banner",
                    "-nostdin",
                    "-loglevel", "info",
                    "-rw_timeout", "15000000",
                    "-i", SOURCE,
                    "-map", "0:v:0",
                    "-map", "0:a:0?",
                    "-c", "copy",
                    "-f", "flv",
                    DESTINATION,
                ]

                self.log_file.write(
                    "\n\n=== INICIO DE RETRANSMISIÓN ===\n"
                )
                self.log_file.flush()

                self.process = subprocess.Popen(
                    command,
                    stdin=subprocess.DEVNULL,
                    stdout=self.log_file,
                    stderr=subprocess.STDOUT,
                    close_fds=True,
                )

                time.sleep(2)

                if self.process.poll() is not None:
                    self.status = "ERROR"
                    self.last_error = (
                        f"FFmpeg terminó con código "
                        f"{self.process.returncode}"
                    )
                else:
                    self.status = "EMITIENDO / CONECTANDO"

            except Exception as error:
                self.status = "ERROR"
                self.last_error = str(error)

    def get_logs(self):
        try:
            with open(LOG_FILE, "r", errors="replace") as file:
                return file.readlines()[-60:]
        except OSError:
            return ["Todavía no hay registros disponibles.\n"]

    def refresh_status(self):
        if self.process is None:
            return self.status

        code = self.process.poll()

        if code is not None:
            self.status = f"ERROR: FFmpeg terminó (código {code})"
        else:
            self.status = "PROCESO ACTIVO"

        return self.status


@st.cache_resource
def get_transmitter():
    return Transmitter()


tx = get_transmitter()

# Inicio automático: no necesita botones.
if not tx.started:
    tx.start()

st.title("📺 Canal C del Zulia")
st.caption("La señal que nos une")
st.subheader("Panel de retransmisión automática")

st.write("**Origen M3U8**")
st.code(SOURCE)

st.write("**Destino RTMP**")
st.code(DESTINATION)

status = tx.refresh_status()

if status == "PROCESO ACTIVO":
    st.success(status)
elif "EMITIENDO" in status:
    st.info(status)
else:
    st.error(status)

if tx.process is not None:
    st.write("PID:", tx.process.pid)

if tx.last_error:
    st.error(tx.last_error)

st.divider()
st.subheader("Últimos registros de FFmpeg")

logs = tx.get_logs()
st.code("".join(logs), language="text")

st.caption(
    "El proceso arranca automáticamente al iniciar la aplicación. "
    "Un proceso activo no garantiza que el servidor RTMP reciba video. "
    "Los reinicios del alojamiento pueden interrumpir la transmisión."
)

# Actualiza el panel periódicamente mientras la página esté abierta.
time.sleep(5)
st.rerun()
