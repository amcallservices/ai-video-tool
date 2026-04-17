"""
================================================================================
AI MULTIMEDIA PRODUCTION SUITE - MASTER v52.0
--------------------------------------------------------------------------------
SISTEMA: Produzione Ibrida Video (15s) / Immagine
MODERAZIONE: Auto-Retry su Errore 500 & Anti-Throttle per Low Credit
ENGINE: Flux Schnell (Immagine) / Luma Dream Machine (Video)
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

# --- 1. CONFIGURAZIONE UI & DESIGN ---
st.set_page_config(page_title="AI Master Studio v52", page_icon="🎬", layout="wide")

st.markdown("""
    <style>
    [data-testid="sidebar-button"] { display: none !important; }
    [data-testid="stSidebar"] {
        min-width: 400px !important;
        background-color: #0d1117;
        border-right: 1px solid #30363d;
    }
    #MainMenu, footer, header, .stAppDeployButton { visibility: hidden; }
    .main { background-color: #0d1117; color: #c9d1d9; }
    
    /* Input Style */
    .stTextArea textarea, .stTextInput input {
        background-color: #161b22 !important;
        color: #58a6ff !important;
        border: 1px solid #30363d !important;
    }

    /* Pulsante Principale */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%);
        color: white; font-size: 1.2rem; font-weight: 800; height: 4.5rem;
        border-radius: 10px; width: 100%; border: none;
        box-shadow: 0 4px 15px rgba(29, 78, 216, 0.3);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CORE: LOGICA DI MONTAGGIO VIDEO ---
def stitch_video_master(urls):
    """Scarica segmenti e crea il file finale da 15s."""
    session_id = str(uuid.uuid4())[:6]
    temp_files = []
    clips = []
    output_name = f"final_master_{session_id}.mp4"
    
    try:
        for i, url in enumerate(urls):
            fname = f"segment_{i}_{session_id}.mp4"
            r = requests.get(url, timeout=60)
            if r.status_code == 200:
                with open(fname, "wb") as f:
                    f.write(r.content)
                temp_files.append(fname)
                clips.append(VideoFileClip(fname))
        
        if clips:
            final = concatenate_videoclips(clips, method="compose")
            final.write_videofile(output_name, codec="libx264", audio=False, logger=None)
            return output_name
    except Exception as e:
        st.error(f"Errore tecnico montaggio: {e}")
    finally:
        for c in clips: c.close()
        for f in temp_files:
            if os.path.exists(f): os.remove(f)
    return None

# --- 3. SESSION STATE ---
if 'translated_prompt' not in st.session_state: st.session_state['translated_prompt'] = ""
if 'final_media' not in st.session_state: st.session_state['final_media'] = None
if 'mode' not in st.session_state: st.session_state['mode'] = "Video"

# --- 4. SIDEBAR CONTROLLI ---
with st.sidebar:
    st.title("💎 STUDIO MASTER")
    st.caption("v52.0 - Flux & Luma Hybrid")
    st.divider()
    
    st.session_state['mode'] = st.radio("Seleziona Tipo Output:", ["Video (15s)", "Immagine HD"])
    
    st.divider()
    it_sub = st.text_input("Soggetto (Italiano):")
    it_act = st.text_area("Azione/Dettagli (Italiano):")
    
    if st.button("🪄 TRADUCI SCRIPT"):
        if it_sub and it_act:
            with st.spinner("Ottimizzazione linguistica..."):
                t = GoogleTranslator(source='it', target='en')
                prompt = f"Professional cinematic shot, {t.translate(it_sub)}, {t.translate(it_act)}, masterpiece quality, 4k, realistic."
                st.session_state['translated_prompt'] = prompt
                st.success("Prompt Pronto!")

    if st.button("🗑️ Reset Totale"):
        st.session_state.clear()
        st.rerun()

# --- 5. WORKSTATION DI PRODUZIONE ---
st.title(f"🚀 Produzione {st.session_state['mode']}")
col_l, col_r = st.columns([1.5, 1])

with col_l:
    prompt_final = st.text_area("Prompt Tecnico (English):", value=st.session_state['translated_prompt'], height=150)
    
    if st.button(f"🔥 GENERA {st.session_state['mode'].upper()}"):
        if not prompt_final:
            st.error("Traduci lo script nella sidebar prima di generare!")
        elif "REPLICATE_API_TOKEN" not in st.secrets:
            st.error("Errore: REPLICATE_API_TOKEN non trovato nei Secrets di Streamlit!")
        else:
            client = replicate.Client(api_token=st.secrets["REPLICATE_API_TOKEN"])
            st.session_state['final_media'] = None
            
            # --- FLUSSO IMMAGINE ---
            if st.session_state['mode'] == "Immagine HD":
                with st.spinner("Rendering Flux Schnell..."):
                    try:
                        out = client.run("black-forest-labs/flux-schnell", input={"prompt": prompt_final})
                        # Gestione sicura URL
                        img_url = str(out[0]) if not hasattr(out[0], 'url') else out[0].url
                        st.session_state['final_media'] = img_url
                        st.balloons()
                    except Exception as e:
                        st.error(f"Errore API Immagine: {e}")
            
            # --- FLUSSO VIDEO ---
            else:
                urls = []
                with st.status("🎬 Avvio Sequenziamento Video...", expanded=True) as status:
                    for i in range(3):
                        clip_success = False
                        retries = 2 # 3 tentativi totali per clip
                        
                        while not clip_success and retries >= 0:
                            try:
                                status.write(f"Produzione clip {i+1}/3 (Tentativo {3-retries})...")
                                prediction = client.predictions.create(
                                    model="luma/dream-machine",
                                    input={"prompt": f"{prompt_final}, part {i+1} of a continuous sequence"}
                                )
                                
                                while prediction.status not in ["succeeded", "failed"]:
                                    time.sleep(5)
                                    prediction.reload()
                                
                                if prediction.status == "succeeded":
                                    # Estrazione URL pulita
                                    res_url = prediction.output
                                    urls.append(str(res_url))
                                    clip_success = True
                                    if i < 2:
                                        status.write("⏳ Pausa anti-throttle (15s)...")
                                        time.sleep(15)
                                else:
                                    retries -= 1
                                    status.write("⚠️ Errore server, riprovo...")
                                    time.sleep(10)
                            except Exception as e:
                                retries -= 1
                                time.sleep(10)
                        
                        if not clip_success:
                            st.error(f"Fallimento critico alla clip {i+1}. Il server Replicate non risponde.")
                            break
                    
                    if len(urls) >= 1:
                        status.write("📦 Montaggio Master in corso...")
                        st.session_state['final_media'] = stitch_video_master(urls)
                        if st.session_state['final_media']: st.balloons()

# --- 6. ANTEPRIMA E DOWNLOAD ---
with col_r:
    st.subheader("🎞️ Risultato")
    res = st.session_state['final_media']
    
    if res:
        if st.session_state['mode'] == "Immagine HD":
            st.image(res, use_column_width=True)
            st.link_button("📥 Apri Immagine Originale", res)
        else:
            if os.path.exists(res):
                st.video(res)
                with open(res, "rb") as f:
                    st.download_button("📥 Scarica Master 15s", f, "video_production.mp4")
            else:
                st.error("Errore: Il file video non è stato trovato sul server locale.")
    else:
        st.info("In attesa di dati dal server AI...")

st.caption("v52.0 - Singularity Edition | Flux & Luma Hybrid | Sidebar Locked")
