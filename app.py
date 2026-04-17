"""
================================================================================
AI VIDEO PRODUCTION SUITE - PLATINUM EDITION v20.0
--------------------------------------------------------------------------------
SISTEMA: Minimax-V1 (Dual-Core GPU)
LOGICA: Google Translate Engine + Extended Storyboard Assistant
LIMITI: 15s (Max per singola clip) - Supporto per montaggio sequenziale.
DESIGN: Sidebar Bloccata tramite CSS Injection.
================================================================================
"""

import streamlit as st
import replicate
import requests
import time
import os
from datetime import datetime
from deep_translator import GoogleTranslator

# ==============================================================================
# 1. ARCHITETTURA UI E DESIGN (SIDEBAR BLOCCATA)
# ==============================================================================

st.set_page_config(
    page_title="AI Video Studio Pro v20",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS per bloccare la sidebar e creare un look professionale
st.markdown("""
    <style>
    [data-testid="sidebar-button"] { display: none !important; }
    [data-testid="stSidebar"] {
        min-width: 450px !important;
        max-width: 450px !important;
        background-color: #0d1117;
        border-right: 1px solid #30363d;
    }
    #MainMenu, footer, header, .stAppDeployButton { visibility: hidden; }
    .main { background-color: #0d1117; }
    
    .stTextArea textarea {
        background-color: #161b22 !important;
        color: #58a6ff !important;
        border: 1px solid #30363d !important;
        font-family: 'SF Mono', monospace;
    }

    div.stButton > button:first-child {
        background: linear-gradient(180deg, #ff4b4b 0%, #8b0000 100%);
        color: white;
        font-size: 1.3rem;
        font-weight: 800;
        height: 5rem;
        border-radius: 10px;
        text-transform: uppercase;
        width: 100%;
        box-shadow: 0 4px 15px rgba(255, 75, 75, 0.3);
    }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 2. MOTORE DI TRADUZIONE E LOGICA PROMPT
# ==============================================================================

def translate_it(text):
    if not text: return ""
    return GoogleTranslator(source='it', target='en').translate(text)

def generate_full_prompt(it_sog, it_azi, style, dur):
    eng_s = translate_it(it_sog)
    eng_a = translate_it(it_azi)
    
    blueprints = {
        "Cinema": "Professional cinematic shot of {s}, {a}. 8k, highly detailed, masterpiece, golden hour lighting.",
        "Sci-Fi": "Futuristic cyberpunk scene of {s}, {a}. Neon lights, volumetric fog, unreal engine 5, ray-tracing.",
        "Doc": "Realistic documentary footage of {s}, {a}. Natural lighting, 4k, handheld stability, authentic textures."
    }
    
    base = blueprints.get(style, blueprints["Cinema"])
    return f"{base.format(s=eng_s, a=eng_a)} Consistent motion for {dur} seconds."

# ==============================================================================
# 3. SIDEBAR: L'ARCHITETTO (BLOOKED)
# ==============================================================================

if 'final_p' not in st.session_state: st.session_state['final_p'] = ""
if 'history' not in st.session_state: st.session_state['history'] = []

with st.sidebar:
    st.title("🎬 PRODUCTION CENTER")
    st.caption("Enterprise Suite v20.0")
    st.divider()
    
    # LIMITI TECNICI
    st.subheader("⏳ Durata della Clip")
    durata_video = st.select_slider("Secondi (Max 15):", options=[6, 10, 15], value=15)
    
    st.divider()
    
    # TRADUTTORE
    st.subheader("🇮🇹 Input in Italiano")
    it_s = st.text_input("Soggetto:", placeholder="Es: Un drago")
    it_a = st.text_area("Azione:", placeholder="Es: Vola sopra un castello sputando fuoco")
    it_st = st.selectbox("Stile:", ["Cinema", "Sci-Fi", "Doc"])

    if st.button("🪄 TRADUCI E GENERA SCRIPT"):
        if it_s and it_a:
            with st.spinner("Traduzione Google in corso..."):
                st.session_state['final_p'] = generate_full_prompt(it_s, it_a, it_st, durata_video)
                st.success("Script pronto in inglese!")
    
    st.divider()
    # GUIDA PER VIDEO LUNGHI
    with st.expander("📖 Come creare video di 1 minuto?"):
        st.write("""
        1. Genera la **Clip 1** (15s).
        2. Fai uno screenshot dell'**ultimo secondo**.
        3. Carica l'immagine (prossimo update) o descrivi accuratamente la posa finale nella **Clip 2**.
        4. Monta le clip insieme.
        """)

# ==============================================================================
# 4. AREA PRODUZIONE
# ==============================================================================

st.title("🚀 Professional AI Video Workstation")
st.markdown("---")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📝 Script Finale (English)")
    prompt_ready = st.text_area("Script tecnico:", value=st.session_state['final_p'], height=250)
    exec_btn = st.button("🔥 AVVIA PRODUZIONE")

with col2:
    st.info(f"**Engine:** Minimax-V1 | **Stato:** Pronto")
    st.warning("I video da 15s richiedono circa 3-5 minuti di elaborazione.")

if exec_btn:
    if not prompt_ready:
        st.error("Usa il traduttore a sinistra!")
    else:
        try:
            client = replicate.Client(api_token=st.secrets["REPLICATE_API_TOKEN"])
            with st.status(f"🎬 Rendering {durata_video}s...", expanded=True) as status:
                prediction = client.predictions.create(
                    model="minimax/video-01",
                    input={"prompt": prompt_ready, "video_length": f"{durata_video}s"}
                )
                while prediction.status not in ["succeeded", "failed", "canceled"]:
                    time.sleep(10)
                    prediction.reload()
                
                if prediction.status == "succeeded":
                    url = prediction.output if isinstance(prediction.output, str) else prediction.output[0]
                    st.video(url)
                    st.session_state['history'].append(url)
                    st.download_button("📥 Scarica Master", requests.get(url).content, "video.mp4")
        except Exception as e:
            st.error(f"Errore: {e}")

# Archivio
if st.session_state['history']:
    st.divider()
    st.subheader("🎞️ Archivio Sessione")
    cols = st.columns(2)
    for idx, vid in enumerate(reversed(st.session_state['history'])):
        cols[idx % 2].video(vid)
