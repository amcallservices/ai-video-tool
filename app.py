"""
================================================================================
AI MULTIMEDIA STUDIO - IRON-CIRCUIT v48.0
--------------------------------------------------------------------------------
SOLUZIONE: Auto-Retry su Errore 500 + Timeout Management.
LOGICA: Gestione resiliente delle clip video e protezione file.
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
st.set_page_config(page_title="AI Studio Iron-Circuit", page_icon="⚡", layout="wide")

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

# --- 2. LOGICA MONTAGGIO (CON CONTROLLO INTEGRITÀ) ---
def stitch_master(urls):
    temp_files = []
    clips = []
    out = "master_output_final.mp4"
    try:
        for i, url in enumerate(urls):
            fname = f"part_{i}.mp4"
            r = requests.get(url, timeout=45)
            if r.status_code == 200:
                with open(fname, "wb") as f: f.write(r.content)
                temp_files.append(fname)
                clips.append(VideoFileClip(fname))
        
        if clips:
            final = concatenate_videoclips(clips, method="compose")
            final.write_videofile(out, codec="libx264", audio=False, logger=None)
            return out
    except Exception as e:
        st.error(f"Errore tecnico nel montaggio: {e}")
    finally:
        for c in clips: c.close()
        for f in temp_files: 
            if os.path.exists(f): os.remove(f)
    return None

# --- 3. SESSION STATE ---
if 'eng_p' not in st.session_state: st.session_state['eng_p'] = ""
if 'media_res' not in st.session_state: st.session_state['media_res'] = None

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("⚡ IRON CONTROL")
    mode = st.radio("Scegli Produzione:", ["Video (15s)", "Immagine"])
    st.divider()
    it_sub = st.text_input("Soggetto (IT):")
    it_act = st.text_area("Azione (IT):")
    
    if st.button("🪄 TRADUCI"):
        if it_sub and it_act:
            ts = GoogleTranslator(source='it', target='en').translate(it_sub)
            ta = GoogleTranslator(source='it', target='en').translate(it_act)
            st.session_state['eng_p'] = f"{ts}, {ta}, cinematic quality, 4k."
            st.success("Pronto!")

# --- 5. PRODUZIONE ---
st.title(f"🚀 Workstation: {mode}")
col_l, col_r = st.columns([2, 1])

with col_l:
    p_ready = st.text_area("Script (EN):", value=st.session_state['eng_p'], height=150)
    
    if st.button("🔥 GENERA ORA"):
        if not p_ready:
            st.error("Traduci lo script!")
        elif "REPLICATE_API_TOKEN" not in st.secrets:
            st.error("Token API mancante!")
        else:
            client = replicate.Client(api_token=st.secrets["REPLICATE_API_TOKEN"])
            st.session_state['media_res'] = None 
            
            if mode == "Immagine":
                with st.spinner("Rendering Flux..."):
                    try:
                        out = client.run("black-forest-labs/flux-schnell", input={"prompt": p_ready})
                        st.session_state['media_res'] = str(out[0])
                    except Exception as e:
                        st.error(f"Errore Server (Immagine): {e}")
            
            else:
                urls = []
                with st.status("🎬 Circuito Video Attivo...", expanded=True) as status:
                    for i in range(3):
                        clip_done = False
                        retries = 2 # Prova 3 volte in totale per ogni clip
                        
                        while not clip_done and retries >= 0:
                            try:
                                status.write(f"Produzione clip {i+1}/3 (Tentativo {3-retries})...")
                                pred = client.predictions.create(
                                    model="luma/dream-machine",
                                    input={"prompt": f"{p_ready}, segment {i+1}"}
                                )
                                while pred.status not in ["succeeded", "failed"]:
                                    time.sleep(5)
                                    pred.reload()
                                
                                if pred.status == "succeeded":
                                    urls.append(str(pred.output))
                                    clip_done = True
                                    if i < 2: time.sleep(15) # Anti-throttle
                                else:
                                    retries -= 1
                                    status.write("⚠️ Errore server, riprovo...")
                                    time.sleep(10)
                            except Exception as e:
                                retries -= 1
                                time.sleep(10)
                        
                        if not clip_done:
                            st.error(f"Impossibile completare la clip {i+1} dopo vari tentativi.")
                            break
                    
                    if len(urls) >= 1:
                        status.write("📦 Unione in corso...")
                        st.session_state['media_res'] = stitch_master(urls)

with col_r:
    st.subheader("🎞️ Anteprima")
    res = st.session_state['media_res']
    
    if res:
        if mode == "Immagine":
            st.image(res)
            st.link_button("📥 Scarica", res)
        else:
            if os.path.exists(res):
                st.video(res)
                with open(res, "rb") as f:
                    st.download_button("📥 Scarica Master", f, "video_15s.mp4")
    else:
        st.info("In attesa di dati stabili dal server...")

st.caption("v48.0 | Iron-Circuit | Auto-Retry Logic")
