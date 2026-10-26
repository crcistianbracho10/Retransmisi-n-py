import streamlit as st
import subprocess
import imageio_ffmpeg

st.set_page_config(page_title="Relay HLS a RTMP", layout="wide")

st.title("📡 Retransmisión de Señal (Stream Copy)")
st.caption("Reenvío de señal sin consumo de CPU mediante FFmpeg integrado.")

DEFAULT_HLS = "https://cristianbracho904.blitz.cloud/hls/index.m3u8"
DEFAULT_RTMP = "rtmp://ssh101.bozztv.com:1935/ssh101/canalczulia"

if "process" not in st.session_state:
    st.session_state.process = None

col1, col2 = st.columns(2)
with col1:
    source_url = st.text_input("Señal Origen (HLS .m3u8)", value=DEFAULT_HLS)
with col2:
    rtmp_url = st.text_input("Destino RTMP", value=DEFAULT_RTMP)

c1, c2, c3 = st.columns([1, 1, 2])

with c1:
    if st.button("▶️ Iniciar Retransmisión", type="primary"):
        if st.session_state.process is not None and st.session_state.process.poll() is None:
            st.warning("La retransmisión ya está en ejecución.")
        else:
            try:
                # Obtenemos la ruta del ejecutable FFmpeg incluido en la librería
                ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

                command = [
                    ffmpeg_exe,
                    "-re",
                    "-i", source_url,
                    "-c", "copy",
                    "-f", "flv",
                    rtmp_url
                ]
                
                st.session_state.process = subprocess.Popen(
                    command,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE
                )
                st.success("Transmisión iniciada correctamente.")
            except Exception as e:
                st.error(f"Error al iniciar FFmpeg: {e}")

with c2:
    if st.button("⏹️ Detener Retransmisión"):
        if st.session_state.process is not None:
            st.session_state.process.terminate()
            st.session_state.process = None
            st.info("Transmisión detenida.")
        else:
            st.warning("No hay ninguna transmisión activa.")

st.subheader("Estado del Proceso")
if st.session_state.process is not None:
    poll_status = st.session_state.process.poll()
    if poll_status is None:
        st.success("🟢 Transmitiendo en vivo (Proceso activo en segundo plano)")
    else:
        st.error(f"🔴 El proceso se ha detenido (Código de salida: {poll_status})")
        _, stderr_data = st.session_state.process.communicate()
        if stderr_data:
            st.code(stderr_data.decode("utf-8", errors="ignore")[-1000:])
else:
    st.info("⚪ Detenido")
