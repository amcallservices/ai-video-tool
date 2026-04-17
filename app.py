"""
================================================================================
AI VIDEO PRODUCTION SUITE - STABLE-PATH v39.0
--------------------------------------------------------------------------------
SOLUZIONE: Usa endpoint canonici per evitare ReplicateError (404/422).
FLUSSO: SDXL (Immagine) -> SVD (Video 3x5s) -> MoviePy (Stitching).
COSTO: Minimo garantito.
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
st.set_page_config(page_title="SVD Stable Studio", page_icon="🎬", layout="wide")

st.markdown("""
    <style>
    [data-testid="sidebar-button"] { display: none !important; }
    [data-testid="stSidebar"] { min-width: 400px !important; background-color: #0d1117; border-right: 1px solid #333; }
    #MainMenu, footer, header, .stAppDeployButton { visibility: hidden; }
    .main { background-color: #0d1117; }
    div.stButton > button:first-child {
        background: linear-gradient(180deg, #6200ea 0%, #311b92 100%);
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
            with open(fname, "wb") as f:
                f.write(requests.get(url).content)
            temp_files.append(fname)
            clips.append(VideoFileClip(fname))
        
        final = concatenate_videoclips(clips, method="compose")
        final.write_videofile(output_name, codec="libx264", audio=False)
        return output_name
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
    st.title("🎨 STABLE BRIDGE")
    st.divider()
    it_sub = st.text_input("Soggetto (IT):")
    it_act = st.text_area("Azione (IT):")
    
    if st.button("🪄 TRADUCI SCRIPT"):
        if it_sub and it_act:
            ts = GoogleTranslator(source='it', target='en').translate(it_sub)
            ta = GoogleTranslator(source='it', target='en').translate(it_act)
            st.session_state['eng_p'] = f"{ts}, {ta}, cinematic, highly detailed, 8k."
            st.success("Prompt pronto!")

# --- 5. AREA PRODUZIONE ---
st.title("🚀 Workstation SVD Low-Cost")
col_l, col_r = st.columns([2, 1])

with col_l:
    prompt_ready = st.text_area("Script Tecnico:", value=st.session_state['eng_p'], height=150)
    
    if st.button("🔥 GENERA VIDEO (15s)"):
        if not prompt_ready:
            st.error("Traduci lo script!")
        elif "REPLICATE_API_TOKEN" not in st.secrets:
            st.error("Token API mancante!")
        else:
            client = replicate.Client(api_token=st.secrets["REPLICATE_API_TOKEN"])
            
            # FASE 1: SDXL (Generazione Immagine) usando il percorso canonico senza ID versione
            with st.status("🖼️ Generazione Immagine Base...", expanded=True):
                try:
                    # Usiamo 'stability-ai/sdxl' come alias stabile
                    output_img = client.run(
                        "stability-ai/sdxl",
                        input={"prompt": prompt_ready}
                    )
                    st.session_state['base_img'] = output_img[0]
                    st.image(st.session_state['base_img'], width=300)
                except Exception as e:
                    st.error(f"Errore SDXL: {e}")
                    st.stop()

            # FASE 2: SVD (Animazione 3x5s)
            urls = []
            bar = st.progress(0)
            for i in range(3):
                with st.status(f"🎬 Animazione Parte {i+1}/3...", expanded=True) as status:
                    prediction = client.predictions.create(
                        model="stability-ai/svd",
                        input={
                            "input_path": st.session_state['base_img'],
                            "motion_bucket_id": 127
                        }
                    )
                    while prediction.status not in ["succeeded", "failed"]:
                        time.sleep(5)
                        prediction.reload()
                    
                    if prediction.status == "succeeded":
                        urls.append(prediction.output[0] if isinstance(prediction.output, list) else prediction.output)
                        status.update(label=f"✅ Clip {i+1} OK", state="complete")
                bar.progress((i + 1) / 3)
            
            # FASE 3: MONTAGGIO
            if len(urls) == 3:
                with st.spinner("📦 Stitching Finale..."):
                    st.session_state['master_v'] = stitch_master(urls)
                    st.balloons()

with col_r:
    st.subheader("🎞️ Risultato Master")
    if st.session_state['master_v']:
        st.video(st.session_state['master_v'])
        with open(st.session_state['master_v'], "rb") as f:
            st.download_button("📥 Scarica Master 15s", f, "svd_master.mp4")

st.caption("v39.0 - Stable-Path | SDXL + SVD + MoviePy")
