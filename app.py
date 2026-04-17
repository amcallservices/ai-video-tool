"""
================================================================================
AI MULTIMEDIA STUDIO - DEEP-SHIELD v47.0
--------------------------------------------------------------------------------
FIX: Gestione errori 500 e protezione FileNotFoundError.
ENGINE: Luma (Video) / Flux (Immagine) - I più stabili del 2026.
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
st.set_page_config(page_title="AI Studio Safe-Mode", page_icon="🛡️", layout="wide")

st.markdown("""
    <style>
    [data-testid="sidebar-button"] { display: none !important; }
    [data-testid="stSidebar"] { min-width: 400px !important; background-color: #0d1117; border-right: 1px solid #333; }
    #MainMenu, footer, header, .stAppDeployButton { visibility: hidden; }
    .main { background-color: #0d1117; }
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);
        color: white; font-size: 1.2rem; font-weight: 800; height: 4rem; border-radius: 8px; width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGICA MONTAGGIO VIDEO (CON PROTEZIONE) ---
def stitch_master(urls):
    temp_files = []
    clips = []
    out = "final_output_master.mp4"
    try:
        for i, url in enumerate(urls):
            fname = f"part_{i}.mp4"
            r = requests.get(url, timeout=30)
            if r.status_code == 200:
                with open(fname, "wb") as f: f.write(r.content)
                temp_files.append(fname)
                clips.append(VideoFileClip(fname))
        
        if clips:
            final = concatenate_videoclips(clips, method="compose")
            final.write_videofile(out, codec="libx264", audio=False, logger=None)
            return out
    except Exception as e:
        st.error(f"Errore durante il montaggio video: {e}")
    finally:
        for c in clips: c.close()
        for f in temp_files: 
            if os.path.exists(f): os.remove(f)
    return None

# --- 3. SESSION STATE ---
if 'eng_p' not in st.session_state: st.session_state['eng_p'] = ""
if 'media_res' not in st.session_state: st.session_state['media_res'] = None
if 'is_image' not in st.session_state: st.session_state['is_image'] = False

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("🛡️ SAFE CONTROL")
    mode = st.radio("Seleziona Output:", ["Video (15s)", "Immagine Singola"])
    st.divider()
    it_sub = st.text_input("Soggetto (IT):")
    it_act = st.text_area("Azione (IT):")
    
    if st.button("🪄 TRADUCI"):
        if it_sub and it_act:
            ts = GoogleTranslator(source='it', target='en').translate(it_sub)
            ta = GoogleTranslator(source='it', target='en').translate(it_act)
            st.session_state['eng_p'] = f"{ts}, {ta}, high quality, cinematic."
            st.success("Testo pronto!")

# --- 5. PRODUZIONE ---
st.title(f"🚀 Workstation: {mode}")
col_l, col_r = st.columns([2, 1])

with col_l:
    p_ready = st.text_area("Script (EN):", value=st.session_state['eng_p'], height=150)
    
    if st.button(f"🔥 AVVIA GENERAZIONE"):
        if not p_ready:
            st.error("Traduci lo script!")
        elif "REPLICATE_API_TOKEN" not in st.secrets:
            st.error("Token API mancante!")
        else:
            client = replicate.Client(api_token=st.secrets["REPLICATE_API_TOKEN"])
            st.session_state['media_res'] = None # Reset precedente
            
            if mode == "Immagine Singola":
                st.session_state['is_image'] = True
                with st.spinner("Creazione immagine..."):
                    try:
                        out = client.run("black-forest-labs/flux-schnell", input={"prompt": p_ready})
                        st.session_state['media_res'] = str(out[0])
                        st.success("Immagine completata!")
                    except Exception as e:
                        st.error(f"Errore Server (500): {e}. Riprova tra poco.")
            
            else:
                st.session_state['is_image'] = False
                urls = []
                with st.status("🎬 Produzione Video...", expanded=True) as status:
                    for i in range(3):
                        try:
                            status.write(f"Clip {i+1}/3...")
                            pred = client.predictions.create(
                                model="luma/dream-machine",
                                input={"prompt": f"{p_ready}, part {i+1}"}
                            )
                            while pred.status not in ["succeeded", "failed"]:
                                time.sleep(5)
                                pred.reload()
                            
                            if pred.status == "succeeded":
                                urls.append(str(pred.output))
                                if i < 2: time.sleep(15) # Anti-throttle
                            else:
                                st.error(f"Il server ha rifiutato la clip {i+1}")
                                break
                        except Exception as e:
                            st.error(f"Errore API Video: {e}")
                            break
                    
                    if len(urls) >= 1:
                        status.write("📦 Stitching...")
                        st.session_state['media_res'] = stitch_master(urls)

with col_r:
    st.subheader("🎞️ Anteprima")
    res = st.session_state['media_res']
    
    if res:
        if st.session_state['is_image']:
            st.image(res)
            st.link_button("📥 Scarica Immagine", res)
        else:
            # PROTEZIONE CRITICA: Controlla se il file esiste prima di aprirlo
            if os.path.exists(res):
                st.video(res)
                with open(res, "rb") as f:
                    st.download_button("📥 Scarica Video", f, "video_15s.mp4")
            else:
                st.warning("Il file video non è stato trovato sul server. Riprova la generazione.")
    else:
        st.info("In attesa di dati validi dal server...")

st.caption("v47.0 | Deep-Shield Edition | Safe Error Handling")
