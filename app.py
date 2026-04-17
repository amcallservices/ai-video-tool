"""
================================================================================
AI MULTIMEDIA STUDIO - THE ROCK v55.0
--------------------------------------------------------------------------------
SOLUZIONE: Passaggio a AnimateDiff (Engine ultra-compatibile).
OBIETTIVO: Eliminare errori 404, 422 e 500 in modo definitivo.
LOGICA: Video 15s (3 clip) con switch Immagine HD (Flux).
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

# --- 1. SETUP UI ---
st.set_page_config(page_title="AI Studio v55 - The Rock", page_icon="🛡️", layout="wide")

st.markdown("""
    <style>
    [data-testid="sidebar-button"] { display: none !important; }
    [data-testid="stSidebar"] { min-width: 400px !important; background-color: #0d1117; border-right: 1px solid #333; }
    #MainMenu, footer, header, .stAppDeployButton { visibility: hidden; }
    .main { background-color: #0d1117; color: #c9d1d9; }
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        color: white; font-size: 1.2rem; font-weight: 800; height: 4.5rem; border-radius: 10px; width: 100%; border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. MONTAGGIO VIDEO ---
def stitch_video_master(urls):
    session_id = str(uuid.uuid4())[:6]
    temp_files, clips = [], []
    out_name = f"master_{session_id}.mp4"
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
        st.error(f"Errore montaggio: {e}")
    finally:
        for c in clips: c.close()
        for f in temp_files: 
            if os.path.exists(f): os.remove(f)
    return None

# --- 3. SIDEBAR ---
if 'eng_p' not in st.session_state: st.session_state['eng_p'] = ""
if 'res' not in st.session_state: st.session_state['res'] = None

with st.sidebar:
    st.title("🛡️ THE ROCK HUB")
    st.caption("v55.0 - High Stability Mode")
    mode = st.radio("Seleziona Output:", ["Video (15s)", "Immagine HD"])
    st.divider()
    it_sub = st.text_input("Soggetto (IT):")
    it_act = st.text_area("Azione (IT):")
    
    if st.button("🪄 TRADUCI SCRIPT"):
        if it_sub and it_act:
            t = GoogleTranslator(source='it', target='en')
            st.session_state['eng_p'] = f"{t.translate(it_sub)}, {t.translate(it_act)}, cinematic lighting, 8k."
            st.success("Prompt Pronto!")

# --- 4. PRODUZIONE ---
st.title(f"🚀 Workstation: {mode}")
col_l, col_r = st.columns([1.5, 1])

with col_l:
    p_final = st.text_area("Prompt Tecnico (EN):", value=st.session_state['eng_p'], height=150)
    
    if st.button("🔥 GENERA ORA"):
        if not p_final:
            st.error("Traduci lo script prima!")
        elif "REPLICATE_API_TOKEN" not in st.secrets:
            st.error("Manca il Token API!")
        else:
            client = replicate.Client(api_token=st.secrets["REPLICATE_API_TOKEN"])
            st.session_state['res'] = None
            
            if mode == "Immagine HD":
                with st.spinner("Creazione Immagine con Flux..."):
                    try:
                        out = client.run("black-forest-labs/flux-schnell", input={"prompt": p_final})
                        st.session_state['res'] = str(out[0])
                    except Exception as e:
                        st.error(f"Errore Immagine: {e}")
            else:
                urls = []
                with st.status("🎬 Sequenziamento Video...", expanded=True) as status:
                    # AnimateDiff: Percorso stabile e universale
                    model_path = "lucataco/animate-diff:be2271c58974859ad77019e44c50d758066e4092070c538a08a28f731e8e2c0e"
                    
                    for i in range(3):
                        try:
                            status.write(f"Produzione clip {i+1}/3...")
                            # Esecuzione diretta per bypassare errori di versione
                            prediction = client.run(
                                model_path,
                                input={
                                    "prompt": f"{p_final}, part {i+1}",
                                    "n_frames": 16
                                }
                            )
                            # AnimateDiff restituisce l'URL direttamente come stringa
                            urls.append(str(prediction))
                            
                            if i < 2: 
                                status.write("⏳ Pausa anti-throttle (12s)...")
                                time.sleep(12)
                        except Exception as e:
                            st.error(f"Errore clip {i+1}: {e}")
                            break
                    
                    if len(urls) >= 1:
                        status.write("📦 Unione dei segmenti...")
                        st.session_state['res'] = stitch_video_master(urls)

with col_r:
    st.subheader("🎞️ Anteprima")
    if st.session_state['res']:
        if mode == "Immagine HD":
            st.image(st.session_state['res'])
            st.link_button("📥 Apri Immagine", st.session_state['res'])
        else:
            if os.path.exists(st.session_state['res']):
                st.video(st.session_state['res'])
                with open(st.session_state['res'], "rb") as f:
                    st.download_button("📥 Scarica Video 15s", f, "video_final.mp4")
    else:
        st.info("In attesa di produzione...")

st.caption("v55.0 - The Rock | Universal Stability | Sidebar Locked")
