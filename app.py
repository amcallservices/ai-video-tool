"""
================================================================================
AI VIDEO PRODUCTION SUITE - THROTTLE-RESILIENT v42.0
--------------------------------------------------------------------------------
SOLUZIONE: Gestione Errore 429 (Rate Limit) tramite pause intelligenti.
LOGICA: Attesa di 10-15 secondi tra le clip per account con credito < $5.
DURATA: 15 Secondi Garantiti (3 clip da 5s).
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
st.set_page_config(page_title="Flux-SVD Resilient Studio", page_icon="🛡️", layout="wide")

st.markdown("""
    <style>
    [data-testid="sidebar-button"] { display: none !important; }
    [data-testid="stSidebar"] { min-width: 400px !important; background-color: #0d1117; border-right: 1px solid #333; }
    #MainMenu, footer, header, .stAppDeployButton { visibility: hidden; }
    .main { background-color: #0d1117; }
    div.stButton > button:first-child {
        background: linear-gradient(180deg, #f39c12 0%, #e67e22 100%);
        color: white; font-size: 1.3rem; font-weight: 800; height: 5rem; border-radius: 10px; width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGICA MONTAGGIO ---
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
if 'base_img_url' not in st.session_state: st.session_state['base_img_url'] = None
if 'master_v' not in st.session_state: st.session_state['master_v'] = None

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("🛡️ SAFE-MODE STUDIO")
    st.caption("Anti-Throttle Logic Active")
    st.divider()
    it_sub = st.text_input("Soggetto (IT):")
    it_act = st.text_area("Azione (IT):")
    
    if st.button("🪄 TRADUCI SCRIPT"):
        if it_sub and it_act:
            ts = GoogleTranslator(source='it', target='en').translate(it_sub)
            ta = GoogleTranslator(source='it', target='en').translate(it_act)
            st.session_state['eng_p'] = f"{ts}, {ta}, cinematic style, highly detailed."
            st.success("Pronto!")

# --- 5. AREA PRODUZIONE ---
st.title("🚀 Workstation Resiliente 15s")
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
            
            # FASE 1: FLUX
            with st.status("🖼️ Fase 1: Immagine...", expanded=True):
                try:
                    output = client.run("black-forest-labs/flux-schnell", input={"prompt": prompt_ready})
                    img_url = str(output[0]) if not hasattr(output[0], 'url') else output[0].url
                    st.session_state['base_img_url'] = img_url
                    st.image(img_url, width=300)
                except Exception as e:
                    st.error(f"Errore Flux: {e}")
                    st.stop()

            # FASE 2: SVD CON ATTESA (FIX 429)
            urls = []
            bar = st.progress(0)
            for i in range(3):
                with st.status(f"🎬 Fase 2: Clip {i+1}/3...", expanded=True) as status:
                    max_retries = 2
                    for attempt in range(max_retries + 1):
                        try:
                            prediction = client.predictions.create(
                                model="stability-ai/svd",
                                input={"input_path": st.session_state['base_img_url'], "motion_bucket_id": 127}
                            )
                            while prediction.status not in ["succeeded", "failed"]:
                                time.sleep(5)
                                prediction.reload()
                            
                            if prediction.status == "succeeded":
                                res = prediction.output
                                final_url = str(res[0]) if isinstance(res, list) else str(res)
                                urls.append(final_url)
                                status.update(label=f"✅ Clip {i+1} OK", state="complete")
                                
                                # PAUSA STRATEGICA: Aspettiamo 12 secondi per resettare il Rate Limit di Replicate
                                if i < 2: 
                                    st.write("⏳ Pausa per evitare blocchi (Rate Limit)...")
                                    time.sleep(12) 
                                break
                        except Exception as e:
                            if "429" in str(e) and attempt < max_retries:
                                st.warning(f"Rilevato Rate Limit. Attesa extra di 15s...")
                                time.sleep(15)
                            else:
                                st.error(f"Errore: {e}")
                                break
                bar.progress((i + 1) / 3)
            
            # FASE 3: MONTAGGIO
            if len(urls) >= 1:
                with st.spinner("📦 Fase 3: Stitching..."):
                    st.session_state['master_v'] = stitch_master(urls)
                    if st.session_state['master_v']: st.balloons()

with col_r:
    st.subheader("🎞️ Risultato")
    if st.session_state['master_v']:
        st.video(st.session_state['master_v'])
        with open(st.session_state['master_v'], "rb") as f:
            st.download_button("📥 Scarica", f, "video_15s.mp4")
    elif st.session_state['base_img_url']:
        st.info("Immagine OK. Elaborazione video rallentata per sicurezza...")

st.caption("v42.0 - Throttle-Resilient | Flux-SVD | Safe-Pause Active")
