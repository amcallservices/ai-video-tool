"""
================================================================================
AI VIDEO PRODUCTION SUITE - FLUX-SVD ULTIMATE v40.0
--------------------------------------------------------------------------------
SOLUZIONE: Passaggio a Flux Schnell per evitare il 404 di SDXL.
FLUSSO: Flux (Immagine) -> SVD (Video 3x5s) -> MoviePy (Stitching).
COSTO: Bassissimo. Qualità immagine superiore.
================================================================================
"""

import streamlit as st
import replicate
import requests
import time
import os
from moviepy.editor import VideoFileClip, concatenate_videoclips
from deep_translator import GoogleTranslator

# --- 1. DESIGN E CONFIGURAZIONE ---
st.set_page_config(page_title="Flux-SVD Video Studio", page_icon="🚀", layout="wide")

st.markdown("""
    <style>
    [data-testid="sidebar-button"] { display: none !important; }
    [data-testid="stSidebar"] { min-width: 400px !important; background-color: #0d1117; border-right: 1px solid #333; }
    #MainMenu, footer, header, .stAppDeployButton { visibility: hidden; }
    .main { background-color: #0d1117; }
    div.stButton > button:first-child {
        background: linear-gradient(180deg, #00d2ff 0%, #3a7bd5 100%);
        color: white; font-size: 1.3rem; font-weight: 800; height: 5rem; border-radius: 10px; width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGICA DI MONTAGGIO (MOVIEPY) ---
def stitch_master(urls):
    temp_files = []
    clips = []
    output_name = "final_master_svd.mp4"
    try:
        for i, url in enumerate(urls):
            fname = f"part_{i}.mp4"
            resp = requests.get(url)
            if resp.status_code == 200:
                with open(fname, "wb") as f:
                    f.write(resp.content)
                temp_files.append(fname)
                clips.append(VideoFileClip(fname))
        
        if clips:
            final = concatenate_videoclips(clips, method="compose")
            final.write_videofile(output_name, codec="libx264", audio=False)
            return output_name
        return None
    finally:
        for c in clips: c.close()
        for f in temp_files: 
            if os.path.exists(f): os.remove(f)

# --- 3. SESSION STATE ---
if 'eng_p' not in st.session_state: st.session_state['eng_p'] = ""
if 'base_img' not in st.session_state: st.session_state['base_img'] = None
if 'master_v' not in st.session_state: st.session_state['master_v'] = None

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("⚡ FLUX + SVD")
    st.caption("Efficienza Massima 2026")
    st.divider()
    it_sub = st.text_input("Soggetto (IT):")
    it_act = st.text_area("Azione (IT):")
    
    if st.button("🪄 TRADUCI SCRIPT"):
        if it_sub and it_act:
            ts = GoogleTranslator(source='it', target='en').translate(it_sub)
            ta = GoogleTranslator(source='it', target='en').translate(it_act)
            st.session_state['eng_p'] = f"{ts}, {ta}, cinematic style, masterwork, highly detailed."
            st.success("Prompt pronto!")

# --- 5. AREA PRODUZIONE ---
st.title("🚀 Workstation Economica 15s")
col_l, col_r = st.columns([2, 1])

with col_l:
    prompt_ready = st.text_area("Script Tecnico:", value=st.session_state['eng_p'], height=150)
    
    if st.button("🔥 GENERA MASTER 15s"):
        if not prompt_ready:
            st.error("Traduci lo script!")
        elif "REPLICATE_API_TOKEN" not in st.secrets:
            st.error("Token API mancante!")
        else:
            client = replicate.Client(api_token=st.secrets["REPLICATE_API_TOKEN"])
            
            # FASE 1: FLUX SCHNELL (Generazione Immagine iper-veloce)
            with st.status("🖼️ Fase 1: Generazione Immagine con Flux...", expanded=True):
                try:
                    # Flux Schnell è molto più stabile e moderno di SDXL
                    output_img = client.run(
                        "black-forest-labs/flux-schnell",
                        input={"prompt": prompt_ready}
                    )
                    # Flux restituisce una lista, prendiamo il primo elemento
                    st.session_state['base_img'] = output_img[0]
                    st.image(st.session_state['base_img'], width=300, caption="Immagine generata")
                except Exception as e:
                    st.error(f"Errore Flux: {e}")
                    st.stop()

            # FASE 2: SVD (Animazione 3 Clip da 5s)
            urls = []
            bar = st.progress(0)
            for i in range(3):
                with st.status(f"🎬 Fase 2: Animazione Clip {i+1}/3...", expanded=True) as status:
                    try:
                        prediction = client.predictions.create(
                            model="stability-ai/svd",
                            input={
                                "input_path": str(st.session_state['base_img']),
                                "motion_bucket_id": 127,
                                "fps": 6
                            }
                        )
                        while prediction.status not in ["succeeded", "failed"]:
                            time.sleep(4)
                            prediction.reload()
                        
                        if prediction.status == "succeeded":
                            # SVD su Replicate può restituire una stringa o una lista
                            res = prediction.output
                            url = res[0] if isinstance(res, list) else res
                            urls.append(url)
                            status.update(label=f"✅ Clip {i+1} OK", state="complete")
                    except Exception as e:
                        st.error(f"Errore SVD Clip {i+1}: {e}")
                bar.progress((i + 1) / 3)
            
            # FASE 3: MONTAGGIO MOVIEPY
            if len(urls) >= 1:
                with st.spinner("📦 Fase 3: Stitching dei segmenti..."):
                    st.session_state['master_v'] = stitch_master(urls)
                    if st.session_state['master_v']:
                        st.balloons()
                    else:
                        st.error("Errore durante il montaggio video.")

with col_r:
    st.subheader("🎞️ Risultato Master 15s")
    if st.session_state['master_v']:
        st.video(st.session_state['master_v'])
        with open(st.session_state['master_v'], "rb") as f:
            st.download_button("📥 Scarica Video Finale", f, "video_15s.mp4")
    elif st.session_state['base_img']:
        st.info("Immagine creata. Animazione in corso...")
    else:
        st.info("In attesa di produzione.")

st.caption("v40.0 - Flux-SVD Ultimate | Economia e Stabilità 2026")
