"""
================================================================================
AI VIDEO PRODUCTION SUITE - THE SURVIVOR v45.0
--------------------------------------------------------------------------------
SOLUZIONE: Passaggio a Wan-2.1 (1.3B) per massima stabilità ed economia.
VANTAGGIO: Text-to-Video diretto (Niente più errori immagine o versioni 404).
DURATA: 3 clip da 5s unite con MoviePy = 15s Reali.
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
st.set_page_config(page_title="AI Video Studio - Survivor", page_icon="🎬", layout="wide")

st.markdown("""
    <style>
    [data-testid="sidebar-button"] { display: none !important; }
    [data-testid="stSidebar"] { min-width: 400px !important; background-color: #0d1117; border-right: 1px solid #333; }
    #MainMenu, footer, header, .stAppDeployButton { visibility: hidden; }
    .main { background-color: #0d1117; }
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #e67e22 0%, #d35400 100%);
        color: white; font-size: 1.3rem; font-weight: 800; height: 5rem; border-radius: 10px; width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGICA MONTAGGIO ---
def stitch_master(urls):
    temp_files = []
    clips = []
    out = "survivor_master.mp4"
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
if 'video_final' not in st.session_state: st.session_state['video_final'] = None

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("🛡️ SURVIVOR ENGINE")
    st.caption("Powered by Wan-2.1 (1.3B)")
    st.divider()
    it_sub = st.text_input("Soggetto (IT):")
    it_act = st.text_area("Azione (IT):")
    
    if st.button("🪄 TRADUCI"):
        if it_sub and it_act:
            ts = GoogleTranslator(source='it', target='en').translate(it_sub)
            ta = GoogleTranslator(source='it', target='en').translate(it_act)
            st.session_state['eng_p'] = f"{ts}, {ta}, high quality, cinematic, 4k."
            st.success("Prompt tradotto!")

# --- 5. AREA PRODUZIONE ---
st.title("🚀 Produzione Resiliente 15s")
col_l, col_r = st.columns([2, 1])

with col_l:
    p_ready = st.text_area("Script Tecnico:", value=st.session_state['eng_p'], height=150)
    
    if st.button("🔥 GENERA VIDEO 15s"):
        if not p_ready:
            st.error("Traduci lo script!")
        elif "REPLICATE_API_TOKEN" not in st.secrets:
            st.error("Token API mancante!")
        else:
            client = replicate.Client(api_token=st.secrets["REPLICATE_API_TOKEN"])
            urls = []
            
            with st.status("🎬 Generazione Clip Sequenziali...", expanded=True) as status:
                for i in range(3):
                    try:
                        status.write(f"Produzione clip {i+1}/3...")
                        # Wan-2.1 1.3B: Economico, Veloce, Text-to-Video
                        prediction = client.predictions.create(
                            model="wan-ai/wan-2.1-t2v-1.3b",
                            input={
                                "prompt": f"{p_ready}, part {i+1}",
                                "aspect_ratio": "16:9"
                            }
                        )
                        
                        while prediction.status not in ["succeeded", "failed"]:
                            time.sleep(5)
                            prediction.reload()
                        
                        if prediction.status == "succeeded":
                            res = prediction.output
                            # Estrazione URL pulito
                            url = res[0] if isinstance(res, list) else res
                            urls.append(str(url))
                            status.write(f"✅ Clip {i+1} completata.")
                            
                            # Pausa anti-throttle per account low-credit
                            if i < 2:
                                status.write("⏳ Pausa di sicurezza per il credito (15s)...")
                                time.sleep(15)
                        else:
                            st.error(f"Errore nella clip {i+1}: {prediction.error}")
                            break
                    except Exception as e:
                        st.error(f"Errore API: {e}")
                        break
            
            if len(urls) >= 1:
                with st.spinner("📦 Unione dei segmenti in corso..."):
                    st.session_state['video_final'] = stitch_master(urls)
                    if st.session_state['video_final']: st.balloons()

with col_r:
    st.subheader("🎞️ Master Risultato")
    if st.session_state['video_final']:
        st.video(st.session_state['video_final'])
        with open(st.session_state['video_final'], "rb") as f:
            st.download_button("📥 Scarica Video 15s", f, "final_video.mp4")
    else:
        st.info("In attesa di produzione...")

st.caption("v45.0 - Survivor Architecture | Wan-2.1 | MoviePy Stitching")
