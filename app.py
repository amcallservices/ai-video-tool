"""
================================================================================
AI VIDEO PRODUCTION SUITE - AUTO-DISCOVERY v44.0
--------------------------------------------------------------------------------
SOLUZIONE: Ricerca automatica dell'ultima versione disponibile (Fix 404).
FLUSSO: Flux Schnell -> SVD (3 Clip) -> MoviePy Stitching.
DURATA: 15 Secondi (3x5s) con pause anti-throttle.
================================================================================
"""

import streamlit as st
import replicate
import requests
import time
import os
from moviepy.editor import VideoFileClip, concatenate_videoclips
from deep_translator import GoogleTranslator

# --- 1. UI SETUP ---
st.set_page_config(page_title="Video Studio v44 - Auto-Discovery", page_icon="🎬", layout="wide")

st.markdown("""
    <style>
    [data-testid="sidebar-button"] { display: none !important; }
    [data-testid="stSidebar"] { min-width: 400px !important; background-color: #0d1117; border-right: 1px solid #333; }
    #MainMenu, footer, header, .stAppDeployButton { visibility: hidden; }
    .main { background-color: #0d1117; }
    div.stButton > button:first-child {
        background: linear-gradient(180deg, #3498db 0%, #2980b9 100%);
        color: white; font-size: 1.3rem; font-weight: 800; height: 5rem; border-radius: 10px; width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGICA MONTAGGIO ---
def stitch_master(urls):
    temp_files = []
    clips = []
    out = "master_output.mp4"
    try:
        for i, url in enumerate(urls):
            fname = f"part_{i}.mp4"
            r = requests.get(url)
            if r.status_code == 200:
                with open(fname, "wb") as f: f.write(r.content)
                temp_files.append(fname)
                clips.append(VideoFileClip(fname))
        if clips:
            final = concatenate_videoclips(clips, method="compose")
            final.write_videofile(out, codec="libx264", audio=False)
            return out
        return None
    finally:
        for c in clips: c.close()
        for f in temp_files: 
            if os.path.exists(f): os.remove(f)

# --- 3. HELPER: TROVA VERSIONE MODELLO ---
def get_latest_version(model_path):
    """Recupera l'ultima versione valida per evitare il 404."""
    try:
        model = replicate.models.get(model_path)
        return model.latest_version.id
    except:
        return None

# --- 4. SESSION STATE ---
if 'eng_p' not in st.session_state: st.session_state['eng_p'] = ""
if 'img_url' not in st.session_state: st.session_state['img_url'] = None
if 'video_res' not in st.session_state: st.session_state['video_res'] = None

# --- 5. SIDEBAR ---
with st.sidebar:
    st.title("🛡️ AUTO-DISCOVERY")
    st.caption("v44.0 - Dynamic Endpoint")
    st.divider()
    it_sub = st.text_input("Soggetto (IT):")
    it_act = st.text_area("Azione (IT):")
    
    if st.button("🪄 TRADUCI"):
        if it_sub and it_act:
            ts = GoogleTranslator(source='it', target='en').translate(it_sub)
            ta = GoogleTranslator(source='it', target='en').translate(it_act)
            st.session_state['eng_p'] = f"{ts}, {ta}, high detail, 8k cinematic."
            st.success("Prompt pronto!")

# --- 6. MAIN WORKSTATION ---
st.title("🚀 Produzione 15s Resiliente")
col_l, col_r = st.columns([2, 1])

with col_l:
    p_ready = st.text_area("Script:", value=st.session_state['eng_p'], height=150)
    
    if st.button("🔥 GENERA MASTER 15s"):
        if not p_ready:
            st.error("Traduci lo script!")
        elif "REPLICATE_API_TOKEN" not in st.secrets:
            st.error("Token API mancante!")
        else:
            client = replicate.Client(api_token=st.secrets["REPLICATE_API_TOKEN"])
            
            # FASE 1: FLUX
            with st.status("🖼️ Fase 1: Immagine...", expanded=True):
                try:
                    out = client.run("black-forest-labs/flux-schnell", input={"prompt": p_ready})
                    st.session_state['img_url'] = str(out[0]) if not hasattr(out[0], 'url') else out[0].url
                    st.image(st.session_state['img_url'], width=300)
                except Exception as e:
                    st.error(f"Errore Flux: {e}")
                    st.stop()

            # FASE 2: SVD AUTO-VERSIONING
            with st.status("🎬 Fase 2: Animazione...", expanded=True) as status:
                svd_version = get_latest_version("stability-ai/svd")
                if not svd_version:
                    st.error("Impossibile trovare una versione valida di SVD. Replicate potrebbe aver cambiato il nome del modello.")
                    st.stop()
                
                urls = []
                for i in range(3):
                    try:
                        status.write(f"Generazione clip {i+1}/3...")
                        prediction = client.predictions.create(
                            version=svd_version,
                            input={"input_path": st.session_state['img_url'], "motion_bucket_id": 127}
                        )
                        while prediction.status not in ["succeeded", "failed"]:
                            time.sleep(5)
                            prediction.reload()
                        
                        if prediction.status == "succeeded":
                            res = prediction.output
                            urls.append(str(res[0]) if isinstance(res, list) else str(res))
                            # Pausa obbligatoria per Rate Limit (credito < $5)
                            if i < 2: 
                                status.write("⏳ Pausa di sicurezza (15s)...")
                                time.sleep(15)
                        else:
                            st.error(f"Errore SVD: {prediction.error}")
                            break
                    except Exception as e:
                        st.error(f"Errore API: {e}")
                        break
            
            # FASE 3: MONTAGGIO
            if len(urls) >= 1:
                with st.spinner("📦 Fase 3: Unione video..."):
                    st.session_state['video_res'] = stitch_master(urls)
                    if st.session_state['video_res']: st.balloons()

with col_r:
    st.subheader("🎞️ Master 15s")
    if st.session_state['video_res']:
        st.video(st.session_state['video_res'])
        with open(st.session_state['video_res'], "rb") as f:
            st.download_button("📥 Scarica", f, "video_final.mp4")
    else:
        st.info("In attesa...")

st.caption("v44.0 - Auto-Discovery | Stable Architecture")
