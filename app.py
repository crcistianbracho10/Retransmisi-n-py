
import streamlit as st
import subprocess
import shutil
import os

st.set_page_config(
    page_title="Canal C del Zulia",
    page_icon="📺"
)

SOURCE = "https://cristianbracho904.blitz.cloud/hls/index.m3u8"
DESTINATION = "rtmp://ssh101.bozz.com/ssh101/canalczulia"

st.title("📺 Canal C del Zulia")
st.caption("Retransmisión M3U8 → RTMP")

if "ffmpeg_process" not in st.session_state:
    st.session_state.ffmpeg_process = None

if "ffmpeg_log" not in st.session_state:
    st.session_state.ffmpeg_log = ""

process = st.session_state.ffmpeg_process

if process is not None and process.poll() is not None:
    st.session_state.ffmpeg_log = "FFmpeg terminó el proceso."
    st.session_state.ffmpeg_process = None
    process = None

if process is None:
    if st.button("Iniciar retransmisión"):
        ffmpeg = shutil.which("ffmpeg")

        if not ffmpeg:
            st.error("FFmpeg no está instalado en el servidor.")
        else:
            command = [
                ffmpeg,
                "-nostdin",
                "-hide_banner",
                "-loglevel", "warning",
                "-i", SOURCE,
                "-map", "0:v:0?",
                "-map", "0:a:0?",
                "-c", "copy",
                "-f", "flv",
                DESTINATION,
            ]

            try:
                process = subprocess.Popen(
                    command,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                st.session_state.ffmpeg_process = process
                st.session_state.ffmpeg_log = (
                    f"Proceso FFmpeg iniciado. PID: {process.pid}"
                )
                st.rerun()
            except Exception as error:
                st.error(f"No se pudo iniciar FFmpeg: {error}")
else:
    st.success("FFmpeg está ejecutándose.")

    if st.button("Detener retransmisión"):
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()

        st.session_state.ffmpeg_process = None
        st.session_state.ffmpeg_log = "Retransmisión detenida."
        st.rerun()

st.info(st.session_state.ffmpeg_log)
