"""
================================================================================
AI VIDEO PRODUCTION SUITE - SVD ECONOMY v36.0
--------------------------------------------------------------------------------
SISTEMA: Stable Video Diffusion (SVD) + MoviePy
VANTAGGIO: Costo ridotto dell'80% rispetto a Minimax.
SOLUZIONE: Stitching di 5 mini-clip per 15-20 secondi totali.
================================================================================
"""

import streamlit as st
import replicate
import requests
import time
import os
from moviepy.editor import VideoFileClip, concatenate_videoclips
from deep_translator import GoogleTranslator

# --- CONFIGURAZIONE UI ---
st.set_page_config(page_title="AI Video Studio - SVD Economy", page_icon="💰", layout="wide")

st.markdown("""
    <style>
    [data-testid="sidebar-button"] { display: none !important; }
    [data-testid="stSidebar"] { min-width: 400px !important; background-color: #0d1117; border-right: 1px solid #333; }
    #MainMenu, footer, header, .stAppDeployButton { visibility: hidden; }
    .main { background-color: #0d1117; }
    div.stButton > button:first-child {
        background: linear-gradient(180deg, #4CAF50 0%, #2E7D32 100%);
        color: white; font-size: 1.3rem; font-weight: 900; height: 5rem; border-radius: 10px; width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# --- MOTORE DI MONTAGGIO ---
def stitch_svd_clips(urls):
    temp_files = []
    video_clips = []
    output_filename = "svd_master_video.mp4"
    try:
        for i, url in enumerate(urls):
            temp_name = f"svd_part_{i}.mp4"
            resp = requests.get(url)
            with open(temp_name, "wb") as f:
                f.write(resp.content)
            temp_files.append(temp_name)
            video_clips.append(VideoFileClip(temp_name))
        
        final_video = concatenate_videoclips(video_clips, method="compose")
        final_video.write_videofile(output_filename, codec="libx264", audio=False)
        return output_filename
    finally:
        for c in video_clips: c.close()
        for f in temp_files: 
            if os.path.exists(f): os.remove(f)

# --- SESSION STATE ---
if 'svd_prompt' not in st.session_state: st.session_state['svd_prompt'] = ""
if 'svd_video' not in st.session_state: st.session_state['svd_video'] = None

# --- SIDEBAR ---
with st.sidebar:
    st.title("💰 SVD ECONOMY")
    st.caption("Massimo risparmio, massima durata")
    st.divider()
    
    st.success("ENGINE: Stable Video Diffusion")
    st.write("Genera 5 clip economiche e le unisce automaticamente.")
    
    it_sub = st.text_input("Soggetto (IT):")
    it_act = st.text_area("Azione (IT):")
    
    if st.button("🪄 TRADUCI SCRIPT"):
        if it_sub and it_act:
            with st.spinner("Traduzione..."):
                ts = GoogleTranslator(source='it', target='en').translate(it_sub)
                ta = GoogleTranslator(source='it', target='en').translate(it_act)
                # SVD lavora meglio con prompt descrittivi e semplici
                st.session_state['svd_prompt'] = f"{ts} {ta}, high quality, detailed, smooth motion."
                st.success("Prompt SVD pronto!")

# --- AREA PRODUZIONE ---
st.title("🚀 Workstation Low-Cost 15s")
st.markdown("---")

col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("📝 Script SVD (English)")
    prompt_ready = st.text_area("Script:", value=st.session_state['svd_prompt'], height=150)
    
    if st.button("🔥 AVVIA PRODUZIONE ECONOMICA"):
        if not prompt_ready:
            st.error("Traduci lo script prima!")
        elif "REPLICATE_API_TOKEN" not in st.secrets:
            st.error("Token API mancante!")
        else:
            urls = []
            client = replicate.Client(api_token=st.secrets["REPLICATE_API_TOKEN"])
            
            # Generiamo 5 clip per coprire circa 15-20 secondi
            bar = st.progress(0)
            for i in range(5):
                with st.status(f"🎬 Batch {i+1}/5 in corso...", expanded=True) as status:
                    # Chiamata al modello SVD
                    prediction = client.predictions.create(
                        model="stability-ai/svd",
                        input={
                            "input_path": "https://replicate.delivery/pbxt/KS9V6ZfQeW38p7aXoYfW5p/rocket.png", # Placeholder se richiesto
                            "prompt": f"{prompt_ready}, sequence {i}",
                            "video_length": "25_frames_with_context"
                        }
                    )
                    while prediction.status not in ["succeeded", "failed"]:
                        time.sleep(4)
                        prediction.reload()
                    
                    if prediction.status == "succeeded":
                        urls.append(prediction.output[0] if isinstance(prediction.output, list) else prediction.output)
                        status.update(label=f"✅ Clip {i+1} OK", state="complete")
                    else:
                        st.error("Errore generazione")
                        break
                bar.progress((i + 1) / 5)
            
            if len(urls) == 5:
                with st.spinner("📦 Montaggio Master MP4..."):
                    master = stitch_svd_clips(urls)
                    st.session_state['svd_video'] = master
                    st.balloons()

with col_right:
    st.subheader("🎞️ Risultato SVD")
    if st.session_state['svd_video']:
        st.video(st.session_state['svd_video'])
        with open(st.session_state['svd_video'], "rb") as f:
            st.download_button("📥 Scarica Video Low-Cost", f, "svd_video.mp4")
    else:
        st.info("Il video apparirà qui.")

st.caption("v36.0 - SVD Economy Architecture | MoviePy Stitching | 2026")
