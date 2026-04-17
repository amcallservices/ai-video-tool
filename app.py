"""
================================================================================
AI MULTIMEDIA STUDIO - MINIMAX ELITE v63.0
--------------------------------------------------------------------------------
ENGINE VIDEO: Minimax (video-01) - Il gold standard per stabilità 2026.
ENGINE IMMAGINE: Flux Schnell - Per anteprime rapide e gratuite.
DURATA: 15s (3 clip da 5s unite con MoviePy).
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
st.set_page_config(page_title="AI Studio Minimax Elite", page_icon="🎬", layout="wide")

st.markdown("""
    <style>
    [data-testid="sidebar-button"] { display: none !important; }
    [data-testid="stSidebar"] { min-width: 380px !important; background-color: #0d1117; border-right: 1px solid #333; }
    #MainMenu, footer, header, .stAppDeployButton { visibility: hidden; }
    .main { background-color: #0d1117; color: #c9d1d9; }
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
        color: white; font-size: 1.1rem; font-weight: 800; height: 4.5rem; border-radius: 10px; width: 100%; border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ENGINE MONTAGGIO ---
def stitch_minimax_clips(urls):
    session_id = str(uuid.uuid4())[:6]
    temp_files, clips = [], []
    out_name = f"minimax_master_{session_id}.mp4"
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

# --- 3. SESSION STATE ---
if 'p_en' not in st.session_state: st.session_state['p_en'] = ""
if 'media_res' not in st.session_state: st.session_state['media_res'] = None

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("🎬 MINIMAX HUB")
    st.caption("v63.0 - Professional Engine")
    mode = st.radio("Seleziona Formato:", ["Video (15s)", "Immagine HD"])
    st.divider()
    it_sub = st.text_input("Soggetto (IT):")
    it_act = st.text_area("Azione (IT):")
    
    if st.button("🪄 TRADUCI SCRIPT"):
        if it_sub and it_act:
            with st.spinner("Ottimizzazione testo..."):
                t = GoogleTranslator(source='it', target='en')
                st.session_state['p_en'] = f"{t.translate(it_sub)}, {t.translate(it_act)}, cinematic lighting, 8k, ultra-realistic."
                st.success("Testo Pronto!")

# --- 5. PRODUZIONE ---
st.title(f"🚀 Workstation: {mode}")
col_l, col_r = st.columns([1.5, 1])

with col_l:
    p_final = st.text_area("Prompt Finale (EN):", value=st.session_state['p_en'], height=150)
    
    if st.button("🔥 GENERA CON MINIMAX"):
        if not p_final:
            st.error("Usa la sidebar per tradurre lo script!")
        elif "REPLICATE_API_TOKEN" not in st.secrets:
            st.error("Manca il Token API nei Secrets!")
        else:
            client = replicate.Client(api_token=st.secrets["REPLICATE_API_TOKEN"])
            st.session_state['media_res'] = None
            
            try:
                if mode == "Immagine HD":
                    with st.spinner("Generazione Flux Schnell..."):
                        # Flux rimane il top per costo/velocità nelle immagini
                        out = client.run("black-forest-labs/flux-schnell", input={"prompt": p_final})
                        st.session_state['media_res'] = str(out[0])
                else:
                    urls = []
                    with st.status("🎬 Produzione Clip Minimax...", expanded=True) as status:
                        for i in range(3):
                            status.write(f"Produzione clip {i+1}/3...")
                            # Minimax richiede un prompt testuale pulito
                            # Usiamo client.run per semplicità e stabilità
                            prediction = client.run(
                                "minimax/video-01",
                                input={"prompt": f"{p_final}, part {i+1}"}
                            )
                            # Minimax restituisce l'URL come stringa o lista di 1 elemento
                            url = prediction[0] if isinstance(prediction, list) else prediction
                            urls.append(str(url))
                            
                            if i < 2: 
                                status.write("⏳ Pausa tecnica (10s)...")
                                time.sleep(10)
                        
                        status.write("📦 Montaggio Master in corso...")
                        st.session_state['media_res'] = stitch_minimax_clips(urls)
                        if st.session_state['media_res']: st.balloons()
            
            except Exception as e:
                st.error(f"Errore critico Replicate: {e}")

with col_r:
    st.subheader("🎞️ Anteprima")
    res = st.session_state['media_res']
    if res:
        if mode == "Immagine HD":
            st.image(res)
            st.link_button("📥 Apri Originale", res)
        else:
            if os.path.exists(res):
                st.video(res)
                with open(res, "rb") as f:
                    st.download_button("📥 Scarica Video Master", f, "video_15s.mp4")
    else:
        st.info("In attesa di produzione...")

st.caption("v63.0 - Minimax Elite | Pro Video Strategy | Sidebar Locked")
