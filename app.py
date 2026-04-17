"""
================================================================================
AI MULTIMEDIA PRODUCTION SUITE - THE SINGULARITY v50.0
--------------------------------------------------------------------------------
SISTEMA: Architettura Modulare Enterprise
ENGINE VIDEO: Luma Dream Machine (Stabile/Economico)
ENGINE IMAGE: Flux Schnell (Iper-realistico/Veloce)
LOGICA: Auto-Retry 500, Anti-Throttle 429, Stitching Video 15s
DESIGN: Sidebar Bloccata (CSS Injection), UI Cinema-Dark
================================================================================
"""

import streamlit as st
import replicate
import requests
import time
import os
import uuid
from datetime import datetime
from moviepy.editor import VideoFileClip, concatenate_videoclips
from deep_translator import GoogleTranslator

# ==============================================================================
# 1. DESIGN SYSTEM & CSS INJECTION (SIDEBAR LOCKED)
# ==============================================================================

st.set_page_config(
    page_title="AI Studio Singularity v50",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

def inject_enterprise_css():
    st.markdown("""
        <style>
        /* BLOCCO SIDEBAR FISICO */
        [data-testid="sidebar-button"] { display: none !important; }
        [data-testid="stSidebar"] {
            min-width: 420px !important;
            max-width: 420px !important;
            background-color: #0d1117;
            border-right: 1px solid #30363d;
        }

        /* UI CLEANUP */
        #MainMenu, footer, header, .stAppDeployButton { visibility: hidden; }
        .main { background-color: #0d1117; color: #c9d1d9; }
        
        /* INPUT STYLING */
        .stTextArea textarea, .stTextInput input {
            background-color: #161b22 !important;
            color: #58a6ff !important;
            border: 1px solid #30363d !important;
            border-radius: 8px !important;
            font-family: 'SF Mono', 'Fira Code', monospace;
        }

        /* MASTER BUTTONS */
        div.stButton > button:first-child {
            background: linear-gradient(135deg, #238636 0%, #2ea043 100%);
            color: white; font-size: 1.1rem; font-weight: 700; padding: 0.75rem 2rem;
            border-radius: 10px; border: none; width: 100%; height: 4rem;
            transition: 0.3s all ease; box-shadow: 0 4px 15px rgba(46, 160, 67, 0.2);
        }
        
        div.stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(46, 160, 67, 0.4);
        }

        /* STATUS CARDS */
        .status-box {
            background: #161b22;
            padding: 15px;
            border-radius: 10px;
            border-left: 5px solid #58a6ff;
            margin: 10px 0;
        }
        </style>
    """, unsafe_allow_html=True)

inject_enterprise_css()

# ==============================================================================
# 2. CORE LOGIC: VIDEO STITCHING ENGINE
# ==============================================================================

def process_video_stitching(urls):
    """
    Gestisce il download e la concatenazione delle clip.
    Implementa la pulizia automatica dei file per prevenire saturazione disco.
    """
    session_id = str(uuid.uuid4())[:8]
    temp_paths = []
    clips = []
    final_output = f"master_{session_id}.mp4"
    
    try:
        for i, url in enumerate(urls):
            tmp_name = f"part_{i}_{session_id}.mp4"
            response = requests.get(url, timeout=60)
            if response.status_code == 200:
                with open(tmp_name, "wb") as f:
                    f.write(response.content)
                temp_paths.append(tmp_name)
                clips.append(VideoFileClip(tmp_name))
        
        if clips:
            # Metodo compose garantisce stabilità se i codec variano leggermente
            final_clip = concatenate_videoclips(clips, method="compose")
            final_clip.write_videofile(final_output, codec="libx264", audio=False, logger=None)
            return final_output
    except Exception as e:
        st.error(f"Errore critico nello Stitching: {e}")
        return None
    finally:
        for c in clips: c.close()
        for f in temp_paths:
            if os.path.exists(f): os.remove(f)

# ==============================================================================
# 3. SESSION STATE & TRADUZIONE
# ==============================================================================

if 'script_en' not in st.session_state: st.session_state['script_en'] = ""
if 'production_res' not in st.session_state: st.session_state['production_res'] = None
if 'media_type' not in st.session_state: st.session_state['media_type'] = "Video"

def run_translation(it_sub, it_act):
    try:
        translator = GoogleTranslator(source='it', target='en')
        t_sub = translator.translate(it_sub)
        t_act = translator.translate(it_act)
        return f"Professional cinematic shot, masterpiece quality. Subject: {t_sub}. Action: {t_act}. Realistic motion, 4k, detailed textures."
    except Exception:
        return f"{it_sub}, {it_act}"

# ==============================================================================
# 4. SIDEBAR: THE CONTROL TOWER
# ==============================================================================

with st.sidebar:
    st.title("💎 SINGULARITY v50")
    st.caption("Advanced AI Production Suite")
    st.divider()
    
    # SELETTORE MODALITÀ
    st.session_state['media_type'] = st.radio(
        "Modalità Output:", 
        ["Video (15s Reali)", "Immagine (Flux)"],
        help="Il video unisce 3 clip per garantire la durata."
    )
    
    st.divider()
    
    # STORYBOARD INPUT
    st.subheader("🇮🇹 Storyboard Italiano")
    it_sub = st.text_input("Soggetto:", placeholder="Es: Un guerriero samurai")
    it_act = st.text_area("Azione/Ambiente:", placeholder="Es: Sguaina la spada sotto i ciliegi in fiore, petali che cadono.")
    
    if st.button("🪄 ELABORA E TRADUCI"):
        if it_sub and it_act:
            with st.spinner("Intelligenza Linguistica in corso..."):
                st.session_state['script_en'] = run_translation(it_sub, it_act)
                st.success("Script Ottimizzato!")
    
    st.divider()
    if st.button("🗑️ RESET SESSIONE"):
        st.session_state.clear()
        st.rerun()

# ==============================================================================
# 5. MAIN WORKSTATION: PRODUCTION AREA
# ==============================================================================

st.title(f"🚀 Produzione {st.session_state['media_type']}")
st.markdown("---")

col_editor, col_viewer = st.columns([1.5, 1])

with col_editor:
    st.subheader("📝 Script Tecnico")
    final_p = st.text_area("Review Prompt (EN):", value=st.session_state['script_en'], height=200)
    
    if st.button("🔥 AVVIA PRODUZIONE"):
        if not final_p:
            st.error("Traduci o inserisci uno script!")
        elif "REPLICATE_API_TOKEN" not in st.secrets:
            st.error("REPLICATE_API_TOKEN non trovato nei Secrets!")
        else:
            client = replicate.Client(api_token=st.secrets["REPLICATE_API_TOKEN"])
            st.session_state['production_res'] = None
            
            # --- FLUSSO IMMAGINE ---
            if st.session_state['media_type'] == "Immagine (Flux)":
                with st.spinner("Rendering Immagine Flux Schnell..."):
                    try:
                        output = client.run("black-forest-labs/flux-schnell", input={"prompt": final_p})
                        st.session_state['production_res'] = str(output[0])
                    except Exception as e:
                        st.error(f"Errore API Immagine: {e}")

            # --- FLUSSO VIDEO (LUMA + AUTO-RETRY + STITCHING) ---
            else:
                urls = []
                with st.status("🎬 Sequenziamento Video Attivo...", expanded=True) as status:
                    for i in range(3):
                        clip_success = False
                        attempts = 3
                        
                        while not clip_success and attempts > 0:
                            try:
                                status.write(f"Generazione Clip {i+1}/3 - Tentativo {4-attempts}...")
                                # Luma Dream Machine: Bilanciamento Costo/Qualità
                                pred = client.predictions.create(
                                    model="luma/dream-machine",
                                    input={"prompt": f"{final_p}, segment {i+1} of a continuous sequence."}
                                )
                                
                                while pred.status not in ["succeeded", "failed", "canceled"]:
                                    time.sleep(5)
                                    pred.reload()
                                
                                if pred.status == "succeeded":
                                    urls.append(str(pred.output))
                                    clip_success = True
                                    if i < 2: 
                                        status.write("⏳ Pausa Anti-Throttle (15s)...")
                                        time.sleep(15) # Protezione credito < $5
                                else:
                                    attempts -= 1
                                    status.write("⚠️ Server Error 500. Raffreddamento...")
                                    time.sleep(10)
                            except Exception as e:
                                attempts -= 1
                                time.sleep(10)
                        
                        if not clip_success:
                            st.error(f"Fallimento definitivo Clip {i+1}. Riprova più tardi.")
                            break
                    
                    if len(urls) >= 1:
                        status.write("📦 Stitching dei segmenti in corso...")
                        st.session_state['production_res'] = process_video_stitching(urls)

# ==============================================================================
# 6. RISULTATI E DOWNLOAD
# ==============================================================================

with col_viewer:
    st.subheader("🎞️ Risultato Finale")
    res = st.session_state['production_res']
    
    if res:
        if "Immagine" in st.session_state['media_type']:
            st.image(res, use_column_width=True)
            st.link_button("📥 Scarica Immagine HD", res)
        else:
            if os.path.exists(res):
                st.video(res)
                with open(res, "rb") as f:
                    st.download_button("📥 Scarica Master 15s", f, "video_production.mp4")
            else:
                st.error("Errore: Il file video è stato generato ma non trovato sul disco.")
    else:
        st.info("In attesa di dati validi dal server...")

# ==============================================================================
# 7. FOOTER
# ==============================================================================
st.markdown("---")
st.caption("v50.0 The Singularity | Enterprise Engine | Luma & Flux Hybrid | Sidebar Locked")
