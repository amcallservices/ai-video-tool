"""
================================================================================
AI MULTIMEDIA STUDIO - FINAL RESILIENCE v53.0
--------------------------------------------------------------------------------
SOLUZIONE: Endpoint WAN-2.1 con ID versione "Locked" per prevenire errore 404.
ENGINE: Wan-2.1 (Video 15s) / Flux Schnell (Immagine HD).
LOGICA: Auto-Stitching MoviePy + Throttling Recovery.
================================================================================
"""

import streamlit as st
import replicate
import requests
import time
import os
import uuid
from moviepy.editor import VideoFileClip, concatenate_videoclips
from deep_translator import GoogleTranslator

# --- 1. CONFIGURAZIONE INTERFACCIA ---
st.set_page_config(page_title="AI Studio Final v53", page_icon="🛡️", layout="wide")

st.markdown("""
    <style>
    [data-testid="sidebar-button"] { display: none !important; }
    [data-testid="stSidebar"] {
        min-width: 400px !important;
        background-color: #0d1117;
        border-right: 1px solid #30363d;
    }
    #MainMenu, footer, header, .stAppDeployButton { visibility: hidden; }
    .main { background-color: #0d1117; color: #c9d1d9; }
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #00c853 0%, #007e33 100%);
        color: white; font-size: 1.2rem; font-weight: 800; height: 4.5rem;
        border-radius: 10px; width: 100%; border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ENGINE DI MONTAGGIO VIDEO ---
def stitch_video_master(urls):
    session_id = str(uuid.uuid4())[:6]
    temp_files, clips = [], []
    out_name = f"master_output_{session_id}.mp4"
    try:
        for i, url in enumerate(urls):
            fname = f"part_{i}_{session_id}.mp4"
            r = requests.get(url, timeout=60)
            if r.status_code == 200:
                with open(fname, "wb") as f: f.write(r.content)
                temp_files.append(fname)
                clips.append(VideoFileClip(fname))
        if clips:
            final = concatenate_videoclips(clips, method="compose")
            final.write_videofile(out_name, codec="libx264", audio=False, logger=None)
            return out_name
    except Exception as e:
        st.error(f"Errore montaggio video: {e}")
    finally:
        for c in clips: c.close()
        for f in temp_files: 
            if os.path.exists(f): os.remove(f)
    return None

# --- 3. GESTIONE STATO ---
if 'prompt_en' not in st.session_state: st.session_state['prompt_en'] = ""
if 'media_result' not in st.session_state: st.session_state['media_result'] = None

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("🛡️ RESILIENCE HUB")
    st.caption("v53.0 - Locked Endpoints")
    mode = st.radio("Seleziona Formato:", ["Video (15s)", "Immagine HD"])
    st.divider()
    it_sub = st.text_input("Soggetto (IT):")
    it_act = st.text_area("Azione (IT):")
    
    if st.button("🪄 TRADUCI SCRIPT"):
        if it_sub and it_act:
            with st.spinner("Traduzione in corso..."):
                t = GoogleTranslator(source='it', target='en')
                st.session_state['prompt_en'] = f"{t.translate(it_sub)}, {t.translate(it_act)}, cinematic lighting, high quality."
                st.success("Script Pronto!")

# --- 5. PRODUZIONE ---
st.title(f"🚀 Workstation: {mode}")
col_l, col_r = st.columns([1.5, 1])

with col_l:
    p_final = st.text_area("Script Tecnico (EN):", value=st.session_state['prompt_en'], height=150)
    
    if st.button("🔥 AVVIA GENERAZIONE"):
        if not p_final:
            st.error("Usa la sidebar per tradurre lo script!")
        elif "REPLICATE_API_TOKEN" not in st.secrets:
            st.error("Token API mancante nei Secrets!")
        else:
            client = replicate.Client(api_token=st.secrets["REPLICATE_API_TOKEN"])
            st.session_state['media_result'] = None
            
            if mode == "Immagine HD":
                with st.spinner("Produzione Immagine Flux..."):
                    try:
                        # Endpoint stabile per Flux Schnell
                        out = client.run("black-forest-labs/flux-schnell", input={"prompt": p_final})
                        st.session_state['media_result'] = str(out[0])
                    except Exception as e:
                        st.error(f"Errore API Immagine: {e}")
            else:
                urls = []
                with st.status("🎬 Sequenziamento Video in corso...", expanded=True) as status:
                    # Utilizziamo l'ID versione HARD-LOCKED di Wan-2.1 per evitare il 404
                    wan_version = "609205315848525b6c3f309b910006720d2b78b0e77d2a5a54e9541a7d16568c"
                    
                    for i in range(3):
                        try:
                            status.write(f"Generazione clip {i+1}/3...")
                            prediction = client.predictions.create(
                                version=wan_version,
                                input={
                                    "prompt": f"{p_final}, sequence part {i+1}",
                                    "aspect_ratio": "16:9"
                                }
                            )
                            while prediction.status not in ["succeeded", "failed"]:
                                time.sleep(5)
                                prediction.reload()
                            
                            if prediction.status == "succeeded":
                                res = prediction.output
                                url = res[0] if isinstance(res, list) else res
                                urls.append(str(url))
                                # Pausa per Rate Limit
                                if i < 2: 
                                    status.write("⏳ Pausa tecnica anti-blocco (15s)...")
                                    time.sleep(15)
                            else:
                                st.error(f"Fallimento clip {i+1}: {prediction.error}")
                                break
                        except Exception as e:
                            st.error(f"Errore critico API Video: {e}")
                            break
                    
                    if len(urls) >= 1:
                        status.write("📦 Montaggio Master in corso...")
                        st.session_state['media_result'] = stitch_video_master(urls)

with col_r:
    st.subheader("🎞️ Anteprima")
    res = st.session_state['media_result']
    if res:
        if mode == "Immagine HD":
            st.image(res)
            st.link_button("📥 Scarica Immagine", res)
        else:
            if os.path.exists(res):
                st.video(res)
                with open(res, "rb") as f:
                    st.download_button("📥 Scarica Video Master", f, "video_15s.mp4")
    else:
        st.info("In attesa di dati dal server AI...")

st.caption("v53.0 - Final Resilience | Version Locked | Sidebar Locked")
