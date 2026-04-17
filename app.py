"""
================================================================================
AI VIDEO PRODUCTION SUITE - SVD-BRIDGE v38.0
--------------------------------------------------------------------------------
SISTEMA: SDXL (Generazione Immagine) + SVD (Animazione) + MoviePy (Stitching)
LOGICA: Risolve l'errore 422 creando l'immagine necessaria prima del video.
DURATA: 3 clip da 5s unite per 15 secondi totali.
COSTO: Estremamente economico.
================================================================================
"""

import streamlit as st
import replicate
import requests
import time
import os
from moviepy.editor import VideoFileClip, concatenate_videoclips
from deep_translator import GoogleTranslator

# --- 1. CONFIGURAZIONE UI ---
st.set_page_config(page_title="SVD Bridge Studio", page_icon="🎨", layout="wide")

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

# --- 2. LOGICA DI MONTAGGIO ---
def stitch_svd_master(urls):
    temp_files = []
    clips = []
    output_name = "svd_master_final.mp4"
    try:
        for i, url in enumerate(urls):
            fname = f"svd_part_{i}.mp4"
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
if 'base_image' not in st.session_state: st.session_state['base_image'] = None
if 'final_v' not in st.session_state: st.session_state['final_v'] = None

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("🎨 SVD BRIDGE")
    st.caption("Text-to-Image-to-Video")
    st.divider()
    
    it_sub = st.text_input("Soggetto (IT):")
    it_act = st.text_area("Azione (IT):")
    
    if st.button("🪄 TRADUCI E PREPARA"):
        if it_sub and it_act:
            ts = GoogleTranslator(source='it', target='en').translate(it_sub)
            ta = GoogleTranslator(source='it', target='en').translate(it_act)
            st.session_state['eng_p'] = f"{ts}, {ta}, cinematic lighting, high resolution, detailed."
            st.success("Prompt pronto!")

# --- 5. AREA PRODUZIONE ---
st.title("🚀 Workstation SVD Economy")
st.markdown("---")

col_l, col_r = st.columns([2, 1])

with col_l:
    prompt_ready = st.text_area("Script:", value=st.session_state['eng_p'], height=150)
    
    if st.button("🔥 AVVIA PRODUZIONE (SDXL + SVD)"):
        if not prompt_ready:
            st.error("Traduci lo script!")
        else:
            client = replicate.Client(api_token=st.secrets["REPLICATE_API_TOKEN"])
            
            # FASE 1: Generazione Immagine Base con SDXL (Necessaria per SVD)
            with st.status("🖼️ Fase 1: Generazione Immagine...", expanded=True):
                image_output = client.run(
                    "stability-ai/sdxl:7762fd39730083977a67bb8e6993d51f8d57167618a9a44f7388b49da873046d",
                    input={"prompt": prompt_ready}
                )
                st.session_state['base_image'] = image_output[0]
                st.image(st.session_state['base_image'], caption="Immagine Base Generata", width=300)

            # FASE 2: Animazione con SVD (3 Clip da 5s)
            urls = []
            bar = st.progress(0)
            for i in range(3):
                with st.status(f"🎬 Fase 2: Animazione Parte {i+1}/3...", expanded=True) as status:
                    prediction = client.predictions.create(
                        model="stability-ai/svd",
                        input={
                            "input_path": st.session_state['base_image'],
                            "video_length": "25_frames_with_context",
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
            
            # FASE 3: Stitching
            if len(urls) == 3:
                with st.spinner("📦 Fase 3: Montaggio Finale..."):
                    master = stitch_svd_master(urls)
                    st.session_state['final_v'] = master
                    st.balloons()

with col_r:
    st.subheader("🎞️ Risultato Finale")
    if st.session_state['final_v']:
        st.video(st.session_state['final_v'])
        with open(st.session_state['final_v'], "rb") as f:
            st.download_button("📥 Scarica Video 15s", f, "svd_master.mp4")
    else:
        st.info("In attesa di produzione.")

st.caption("v38.0 - SVD Bridge | SDXL Integrated | MoviePy Stitching")
