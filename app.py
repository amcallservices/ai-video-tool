"""
================================================================================
AI MULTIMEDIA STUDIO - THE FINAL CHOICE v59.0
--------------------------------------------------------------------------------
ENGINE VIDEO: Minimax (video-01) - Economico, stabile, alta compatibilità.
ENGINE IMMAGINE: Flux Schnell - Il re della stabilità.
DURATA: 15s (3 clip da 5s ciascuna).
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
st.set_page_config(page_title="AI Studio v59", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    [data-testid="sidebar-button"] { display: none !important; }
    [data-testid="stSidebar"] { min-width: 400px !important; background-color: #0d1117; border-right: 1px solid #30363d; }
    #MainMenu, footer, header, .stAppDeployButton { visibility: hidden; }
    .main { background-color: #0d1117; color: #c9d1d9; }
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #00c853 0%, #007e33 100%);
        color: white; font-size: 1.2rem; font-weight: 800; height: 4.5rem; border-radius: 10px; width: 100%; border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ENGINE MONTAGGIO ---
def stitch_master(urls):
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

# --- 3. LOGICA DI PROCESSO ---
if 'p_en' not in st.session_state: st.session_state['p_en'] = ""
if 'res_media' not in st.session_state: st.session_state['res_media'] = None

with st.sidebar:
    st.title("⚡ MINIMAX ENGINE")
    st.caption("v59.0 - High Compatibility")
    mode = st.radio("Seleziona Output:", ["Video (15s)", "Immagine HD"])
    st.divider()
    it_sub = st.text_input("Soggetto (IT):")
    it_act = st.text_area("Azione (IT):")
    
    if st.button("🪄 TRADUCI SCRIPT"):
        if it_sub and it_act:
            t = GoogleTranslator(source='it', target='en')
            st.session_state['p_en'] = f"{t.translate(it_sub)}, {t.translate(it_act)}, cinematic lighting, high quality."
            st.success("Testo Tradotto!")

# --- 4. AREA PRODUZIONE ---
st.title(f"🚀 Workstation: {mode}")
col_l, col_r = st.columns([1.5, 1])

with col_l:
    p_final = st.text_area("Prompt (EN):", value=st.session_state['p_en'], height=150)
    
    if st.button("🔥 AVVIA"):
        if not p_final:
            st.error("Traduci lo script!")
        elif "REPLICATE_API_TOKEN" not in st.secrets:
            st.error("Manca il Token API!")
        else:
            client = replicate.Client(api_token=st.secrets["REPLICATE_API_TOKEN"])
            st.session_state['res_media'] = None
            
            if mode == "Immagine HD":
                with st.spinner("Creazione Immagine (Flux)..."):
                    try:
                        out = client.run("black-forest-labs/flux-schnell", input={"prompt": p_final})
                        st.session_state['res_media'] = str(out[0])
                    except Exception as e:
                        st.error(f"Errore: {e}")
            else:
                urls = []
                with st.status("🎬 Generazione Video (Minimax)...", expanded=True) as status:
                    # MINIMAX VIDEO-01: Molto più economico e stabile di Luma
                    model_path = "minimax/video-01"
                    
                    for i in range(3):
                        try:
                            status.write(f"Produzione clip {i+1}/3...")
                            # Metodo run diretto: il più sicuro contro errori 422
                            prediction = client.run(
                                model_path,
                                input={"prompt": f"{p_final}, part {i+1}"}
                            )
                            # Minimax restituisce l'URL direttamente
                            urls.append(str(prediction))
                            
                            if i < 2: 
                                status.write("⏳ Pausa anti-throttle (12s)...")
                                time.sleep(12)
                        except Exception as e:
                            st.error(f"Errore clip {i+1}: {e}")
                            break
                    
                    if len(urls) >= 1:
                        status.write("📦 Montaggio Master...")
                        st.session_state['res_media'] = stitch_master(urls)

with col_r:
    st.subheader("🎞️ Anteprima")
    res = st.session_state['res_media']
    if res:
        if mode == "Immagine HD":
            st.image(res)
            st.link_button("📥 Scarica", res)
        else:
            if os.path.exists(res):
                st.video(res)
                with open(res, "rb") as f:
                    st.download_button("📥 Scarica Video Master", f, "video_final.mp4")
    else:
        st.info("In attesa...")

st.caption("v59.0 - Minimax Strategy | Economic & Stable | Sidebar Locked")
