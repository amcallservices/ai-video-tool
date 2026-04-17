"""
================================================================================
AI MULTIMEDIA STUDIO - THE FINAL GATEWAY v56.0
--------------------------------------------------------------------------------
SOLUZIONE: Chiamata dinamica all'ultima versione (Fix 422/404).
MOTORE VIDEO: AnimateDiff (Ultra-stabile / Low-cost).
MOTORE IMMAGINE: Flux Schnell (Top Quality).
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
st.set_page_config(page_title="AI Studio v56", page_icon="💎", layout="wide")

st.markdown("""
    <style>
    [data-testid="sidebar-button"] { display: none !important; }
    [data-testid="stSidebar"] { min-width: 400px !important; background-color: #0d1117; border-right: 1px solid #30363d; }
    #MainMenu, footer, header, .stAppDeployButton { visibility: hidden; }
    .main { background-color: #0d1117; color: #c9d1d9; }
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #6366f1 0%, #4338ca 100%);
        color: white; font-size: 1.2rem; font-weight: 800; height: 4.5rem; border-radius: 10px; width: 100%; border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGICA MONTAGGIO ---
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
if 'translated_p' not in st.session_state: st.session_state['translated_p'] = ""
if 'media_res' not in st.session_state: st.session_state['media_res'] = None

with st.sidebar:
    st.title("💎 GATEWAY HUB")
    st.caption("v56.0 - Dynamic Stability Mode")
    mode = st.radio("Scegli Produzione:", ["Video (15s)", "Immagine HD"])
    st.divider()
    it_sub = st.text_input("Soggetto (IT):")
    it_act = st.text_area("Azione (IT):")
    
    if st.button("🪄 TRADUCI SCRIPT"):
        if it_sub and it_act:
            t = GoogleTranslator(source='it', target='en')
            st.session_state['translated_p'] = f"{t.translate(it_sub)}, {t.translate(it_act)}, cinematic lighting, 8k quality."
            st.success("Testo Tradotto!")

# --- 4. AREA PRODUZIONE ---
st.title(f"🚀 Workstation: {mode}")
col_l, col_r = st.columns([1.5, 1])

with col_l:
    p_final = st.text_area("Prompt Finale (EN):", value=st.session_state['translated_p'], height=150)
    
    if st.button("🔥 AVVIA GENERAZIONE"):
        if not p_final:
            st.error("Traduci lo script prima!")
        elif "REPLICATE_API_TOKEN" not in st.secrets:
            st.error("Token API mancante!")
        else:
            client = replicate.Client(api_token=st.secrets["REPLICATE_API_TOKEN"])
            st.session_state['media_res'] = None
            
            if mode == "Immagine HD":
                with st.spinner("Creazione Immagine (Flux)..."):
                    try:
                        # Flux Schnell è l'engine più stabile per le immagini
                        out = client.run("black-forest-labs/flux-schnell", input={"prompt": p_final})
                        st.session_state['media_res'] = str(out[0])
                    except Exception as e:
                        st.error(f"Errore Immagine: {e}")
            else:
                urls = []
                with st.status("🎬 Generazione Video Sequenziale...", expanded=True) as status:
                    # Usiamo il percorso corto per far decidere a Replicate la versione migliore
                    model_slug = "lucataco/animate-diff"
                    
                    for i in range(3):
                        try:
                            status.write(f"Produzione clip {i+1}/3...")
                            # Chiamata dinamica che evita l'errore 422 (Invalid Version)
                            prediction = client.run(
                                model_slug,
                                input={
                                    "prompt": f"{p_final}, part {i+1}",
                                    "n_frames": 16
                                }
                            )
                            # Estrazione URL sicura
                            url = prediction[0] if isinstance(prediction, list) else prediction
                            urls.append(str(url))
                            
                            if i < 2: 
                                status.write("⏳ Pausa di sicurezza (12s)...")
                                time.sleep(12)
                        except Exception as e:
                            st.error(f"Errore alla clip {i+1}: {e}")
                            break
                    
                    if len(urls) >= 1:
                        status.write("📦 Montaggio Master...")
                        st.session_state['media_res'] = stitch_video_master(urls)

with col_r:
    st.subheader("🎞️ Risultato")
    res = st.session_state['media_res']
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
        st.info("In attesa di produzione...")

st.caption("v56.0 - The Final Gateway | Dynamic Model Calling | Sidebar Locked")
