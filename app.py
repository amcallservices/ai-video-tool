"""
================================================================================
AI MULTIMEDIA STUDIO - HYBRID-STABLE v46.0
--------------------------------------------------------------------------------
SOLUZIONE: Switch Video/Immagine + Endpoint Luma/Flux ultra-stabili.
LOGICA: Gestione automatica del credito e delle pause anti-throttle.
================================================================================
"""

import streamlit as st
import replicate
import requests
import time
import os
from moviepy.editor import VideoFileClip, concatenate_videoclips
from deep_translator import GoogleTranslator

# --- 1. SETUP UI ---
st.set_page_config(page_title="AI Studio - Video & Image", page_icon="🎬", layout="wide")

st.markdown("""
    <style>
    [data-testid="sidebar-button"] { display: none !important; }
    [data-testid="stSidebar"] { min-width: 400px !important; background-color: #0d1117; border-right: 1px solid #333; }
    #MainMenu, footer, header, .stAppDeployButton { visibility: hidden; }
    .main { background-color: #0d1117; }
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #3498db 0%, #1d4ed8 100%);
        color: white; font-size: 1.2rem; font-weight: 800; height: 4rem; border-radius: 8px; width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGICA MONTAGGIO VIDEO ---
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

# --- 3. SESSION STATE ---
if 'eng_p' not in st.session_state: st.session_state['eng_p'] = ""
if 'media_res' not in st.session_state: st.session_state['media_res'] = None

# --- 4. SIDEBAR (Configurazione) ---
with st.sidebar:
    st.title("🛠️ STUDIO CONFIG")
    st.divider()
    
    # SELETTORE MODALITÀ
    mode = st.radio("Cosa vuoi generare?", ["Video (15s)", "Immagine Singola"], index=0)
    
    st.divider()
    it_sub = st.text_input("Soggetto (IT):")
    it_act = st.text_area("Dettagli/Azione (IT):")
    
    if st.button("🪄 TRADUCI SCRIPT"):
        if it_sub and it_act:
            with st.spinner("Traduzione..."):
                ts = GoogleTranslator(source='it', target='en').translate(it_sub)
                ta = GoogleTranslator(source='it', target='en').translate(it_act)
                st.session_state['eng_p'] = f"{ts}, {ta}, professional lighting, 4k, high quality."
                st.success("Pronto!")

# --- 5. AREA PRODUZIONE ---
st.title(f"🚀 Workstation: {mode}")
col_l, col_r = st.columns([2, 1])

with col_l:
    p_ready = st.text_area("Script Finale (EN):", value=st.session_state['eng_p'], height=150)
    
    if st.button(f"🔥 GENERA {mode.upper()}"):
        if not p_ready:
            st.error("Traduci lo script prima!")
        elif "REPLICATE_API_TOKEN" not in st.secrets:
            st.error("Token API mancante nei Secrets!")
        else:
            client = replicate.Client(api_token=st.secrets["REPLICATE_API_TOKEN"])
            
            # --- LOGICA IMMAGINE ---
            if mode == "Immagine Singola":
                with st.status("🖼️ Generazione Immagine con Flux...", expanded=True):
                    try:
                        out = client.run("black-forest-labs/flux-schnell", input={"prompt": p_ready})
                        st.session_state['media_res'] = str(out[0]) if not hasattr(out[0], 'url') else out[0].url
                        st.success("Immagine creata!")
                    except Exception as e:
                        st.error(f"Errore: {e}")

            # --- LOGICA VIDEO ---
            else:
                urls = []
                with st.status("🎬 Generazione Video 15s (3 Clip)...", expanded=True) as status:
                    for i in range(3):
                        try:
                            status.write(f"Produzione clip {i+1}/3...")
                            # Usiamo Luma Dream Machine: ultra-stabile
                            prediction = client.predictions.create(
                                model="luma/dream-machine",
                                input={"prompt": f"{p_ready}, cinematic movement, part {i+1}"}
                            )
                            while prediction.status not in ["succeeded", "failed"]:
                                time.sleep(5)
                                prediction.reload()
                            
                            if prediction.status == "succeeded":
                                urls.append(str(prediction.output))
                                # Pausa per Rate Limit
                                if i < 2:
                                    status.write("⏳ Pausa sicurezza credito (15s)...")
                                    time.sleep(15)
                            else:
                                st.error(f"Errore Clip {i+1}")
                                break
                        except Exception as e:
                            st.error(f"Errore API: {e}")
                            break
                    
                    if len(urls) >= 1:
                        status.write("📦 Montaggio finale...")
                        st.session_state['media_res'] = stitch_master(urls)
                        st.balloons()

with col_r:
    st.subheader("🎞️ Anteprima Risultato")
    if st.session_state['media_res']:
        if mode == "Immagine Singola":
            st.image(st.session_state['media_res'])
            st.link_button("📥 Apri Immagine", st.session_state['media_res'])
        else:
            st.video(st.session_state['media_res'])
            with open(st.session_state['media_res'], "rb") as f:
                st.download_button("📥 Scarica Video", f, "video_15s.mp4")
    else:
        st.info("Il risultato apparirà qui dopo la generazione.")

st.caption("v46.0 | Hybrid Studio | Flux & Luma Integration")
