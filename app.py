"""
================================================================================
AI VIDEO PRODUCTION SUITE - ULTRA-STITCHER PRO v35.0
--------------------------------------------------------------------------------
SISTEMA: Minimax-V1 + MoviePy Auto-Stitching
SOLUZIONE: Generazione 3x5s e unione automatica per ottenere 15s reali.
DESIGN: Sidebar Bloccata, Interfaccia Cinema-Dark, Google Translate integrato.
================================================================================
"""

import streamlit as st
import replicate
import requests
import time
import os
from moviepy.editor import VideoFileClip, concatenate_videoclips
from deep_translator import GoogleTranslator

# --- 1. CONFIGURAZIONE UI E CSS ---
st.set_page_config(page_title="AI Video Studio - Ultra-Stitcher", page_icon="🎬", layout="wide")

st.markdown("""
    <style>
    /* BLOCCA SIDEBAR */
    [data-testid="sidebar-button"] { display: none !important; }
    [data-testid="stSidebar"] {
        min-width: 400px !important;
        background-color: #0d1117;
        border-right: 1px solid #333;
    }
    #MainMenu, footer, header, .stAppDeployButton { visibility: hidden; }
    .main { background-color: #0d1117; }
    
    /* Input Style Terminal */
    .stTextArea textarea {
        background-color: #161b22 !important;
        color: #58a6ff !important;
        border: 1px solid #30363d !important;
        font-family: 'SF Mono', monospace;
    }

    /* Pulsante Produzione */
    div.stButton > button:first-child {
        background: linear-gradient(180deg, #ff4b4b 0%, #8b0000 100%);
        color: white; font-size: 1.3rem; font-weight: 900; height: 5rem;
        border-radius: 10px; text-transform: uppercase; width: 100%;
        box-shadow: 0 4px 15px rgba(255, 75, 75, 0.3);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGICA DI STITCHING (MONTAGGIO AUTOMATICO) ---
def stitch_video_segments(urls, output_filename="final_video_15s.mp4"):
    """Scarica le clip, le unisce e pulisce i file temporanei."""
    temp_files = []
    video_clips = []
    
    try:
        for i, url in enumerate(urls):
            temp_name = f"part_{i}.mp4"
            # Download del segmento
            resp = requests.get(url)
            with open(temp_name, "wb") as f:
                f.write(resp.content)
            temp_files.append(temp_name)
            
            # Creazione oggetto clip
            video_clips.append(VideoFileClip(temp_name))
        
        # Unione delle clip
        final_video = concatenate_videoclips(video_clips, method="compose")
        final_video.write_videofile(output_filename, codec="libx264", audio=False)
        return output_filename
    
    finally:
        # Pulizia rigorosa
        for clip in video_clips:
            clip.close()
        for f in temp_files:
            if os.path.exists(f):
                os.remove(f)

# --- 3. SESSION STATE ---
if 'eng_prompt' not in st.session_state: st.session_state['eng_prompt'] = ""
if 'final_video_path' not in st.session_state: st.session_state['final_video_path'] = None

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("🛡️ ULTRA-STITCHER")
    st.caption("Soluzione Definitiva per i 15 Secondi")
    st.divider()
    
    st.info("💡 Questo tool genera 3 clip da 5 secondi e le unisce per garantirti un video da 15 secondi reali.")
    
    it_sub = st.text_input("Soggetto (IT):", placeholder="Es: Un astronauta")
    it_act = st.text_area("Azione (IT):", placeholder="Es: Cammina sulla luna e pianta una bandiera")
    
    if st.button("🪄 TRADUCI SCRIPT"):
        if it_sub and it_act:
            with st.spinner("Traduzione Google..."):
                eng_s = GoogleTranslator(source='it', target='en').translate(it_sub)
                eng_a = GoogleTranslator(source='it', target='en').translate(it_act)
                st.session_state['eng_prompt'] = f"Cinematic 8k shot of {eng_s}, {eng_a}. Highly detailed, 35mm lens, smooth motion."
                st.success("Pronto per la produzione!")

    if st.button("Reset Sessione"):
        st.session_state.clear()
        st.rerun()

# --- 5. AREA PRODUZIONE ---
st.title("🚀 Workstation Video 15s")
st.markdown("---")

col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("📝 Script Tecnico (English)")
    prompt_ready = st.text_area("Script per l'AI:", value=st.session_state['eng_prompt'], height=200)
    
    if st.button("🔥 AVVIA PRODUZIONE E UNIONE"):
        if not prompt_ready:
            st.error("Usa la sidebar per tradurre lo script!")
        elif "REPLICATE_API_TOKEN" not in st.secrets:
            st.error("Token API mancante nei Secrets!")
        else:
            urls = []
            client = replicate.Client(api_token=st.secrets["REPLICATE_API_TOKEN"])
            
            # Generazione di 3 clip sequenziali
            progress_bar = st.progress(0)
            for i in range(3):
                with st.status(f"🎬 Generazione Parte {i+1} di 3...", expanded=True) as status:
                    # Usiamo i 5s che sono lo standard stabile di Minimax
                    prediction = client.predictions.create(
                        model="minimax/video-01",
                        input={"prompt": f"{prompt_ready}, sequence part {i+1}", "video_length": "5s"}
                    )
                    while prediction.status not in ["succeeded", "failed"]:
                        time.sleep(5)
                        prediction.reload()
                    
                    if prediction.status == "succeeded":
                        url = prediction.output[0] if isinstance(prediction.output, list) else prediction.output
                        urls.append(url)
                        status.update(label=f"✅ Parte {i+1} Pronta!", state="complete")
                    else:
                        st.error(f"Errore nella parte {i+1}")
                        break
                progress_bar.progress((i + 1) / 3)
            
            if len(urls) == 3:
                with st.spinner("📦 Stitching dei video in corso..."):
                    master_path = stitch_video_segments(urls)
                    st.session_state['final_video_path'] = master_path
                    st.balloons()

with col_right:
    st.subheader("🎞️ Risultato Master")
    if st.session_state['final_video_path']:
        st.video(st.session_state['final_video_path'])
        with open(st.session_state['final_video_path'], "rb") as f:
            st.download_button("📥 Scarica Master 15s", f, "video_finale_15s.mp4")
    else:
        st.info("Il video unito apparirà qui.")

st.caption("v35.0 - Ultra-Stitcher Pro | Minimax Dedicated | Sidebar Locked")
