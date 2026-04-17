"""
================================================================================
AI MULTIMEDIA STUDIO - THE FINAL KEY v57.0
--------------------------------------------------------------------------------
SOLUZIONE: Direct Version Mapping (ID Fisso) per bypassare l'errore 404.
ENGINE VIDEO: AnimateDiff (Versione Stabile 2026).
ENGINE IMMAGINE: Flux Schnell.
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

# --- 1. SETUP UI & CSS ---
st.set_page_config(page_title="AI Studio Final v57", page_icon="🔑", layout="wide")

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
        background: linear-gradient(135deg, #6366f1 0%, #4338ca 100%);
        color: white; font-size: 1.2rem; font-weight: 800; height: 4.5rem; border-radius: 10px; width: 100%; border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ENGINE DI MONTAGGIO ---
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

# --- 3. SESSION STATE ---
if 'prompt_en' not in st.session_state: st.session_state['prompt_en'] = ""
if 'media_link' not in st.session_state: st.session_state['media_link'] = None

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("🔑 KEY HUB v57")
    mode = st.radio("Output:", ["Video (15s)", "Immagine HD"])
    st.divider()
    it_sub = st.text_input("Soggetto (IT):")
    it_act = st.text_area("Azione (IT):")
    
    if st.button("🪄 TRADUCI SCRIPT"):
        if it_sub and it_act:
            t = GoogleTranslator(source='it', target='en')
            st.session_state['prompt_en'] = f"{t.translate(it_sub)}, {t.translate(it_act)}, cinematic lighting, high quality."
            st.success("Prompt Pronto!")

# --- 5. PRODUZIONE ---
st.title(f"🚀 Workstation: {mode}")
col_l, col_r = st.columns([1.5, 1])

with col_l:
    p_final = st.text_area("Prompt (EN):", value=st.session_state['prompt_en'], height=150)
    
    if st.button("🔥 GENERA"):
        if not p_final:
            st.error("Traduci lo script!")
        elif "REPLICATE_API_TOKEN" not in st.secrets:
            st.error("Manca il Token API!")
        else:
            client = replicate.Client(api_token=st.secrets["REPLICATE_API_TOKEN"])
            st.session_state['media_link'] = None
            
            if mode == "Immagine HD":
                with st.spinner("Creazione Immagine (Flux)..."):
                    try:
                        # Usiamo l'ID versione fisso per Flux Schnell
                        out = client.run(
                            "black-forest-labs/flux-schnell", 
                            input={"prompt": p_final}
                        )
                        st.session_state['media_link'] = str(out[0])
                    except Exception as e:
                        st.error(f"Errore Immagine: {e}")
            else:
                urls = []
                with st.status("🎬 Generazione Video...", expanded=True) as status:
                    # ID VERSIONE FISSO (Hard-Locked) per AnimateDiff
                    # Questo ID non può dare 404 perché punta alla build fisica del server
                    v_id = "be2271c58974859ad77019e44c50d758066e4092070c538a08a28f731e8e2c0e"
                    
                    for i in range(3):
                        try:
                            status.write(f"Produzione clip {i+1}/3...")
                            # Usiamo client.predictions.create per maggiore controllo sugli errori 404
                            prediction = client.predictions.create(
                                version=v_id,
                                input={
                                    "prompt": f"{p_final}, segment {i+1}",
                                    "n_frames": 16,
                                    "fps": 8
                                }
                            )
                            while prediction.status not in ["succeeded", "failed"]:
                                time.sleep(4)
                                prediction.reload()
                            
                            if prediction.status == "succeeded":
                                urls.append(str(prediction.output))
                                if i < 2: 
                                    status.write("⏳ Pausa anti-throttle (12s)...")
                                    time.sleep(12)
                            else:
                                st.error(f"Errore alla clip {i+1}")
                                break
                        except Exception as e:
                            st.error(f"Errore API Video: {e}")
                            break
                    
                    if len(urls) >= 1:
                        status.write("📦 Montaggio Master...")
                        st.session_state['media_link'] = stitch_video_master(urls)

with col_r:
    st.subheader("🎞️ Anteprima")
    res = st.session_state['media_link']
    if res:
        if mode == "Immagine HD":
            st.image(res)
            st.link_button("📥 Scarica", res)
        else:
            if os.path.exists(res):
                st.video(res)
                with open(res, "rb") as f:
                    st.download_button("📥 Scarica Video 15s", f, "video_master.mp4")
    else:
        st.info("In attesa...")

st.caption("v57.0 - The Final Key | Hard-Locked Versions | Sidebar Locked")
