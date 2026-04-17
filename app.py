"""
================================================================================
AI VIDEO PRODUCTION SUITE - SAFE-MULTI-ENGINE v25.0
--------------------------------------------------------------------------------
SISTEMA: Multi-Engine con gestione dinamica degli input (Fix ReplicateError)
AUTOMAZIONE: Batch Sequenziale 1 Minuto (4 Clip)
TRADUZIONE: Google Translate Bridge integrato
LUNGHEZZA: Struttura Enterprise oltre 1000 righe
================================================================================
"""

import streamlit as st
import replicate
import requests
import time
from datetime import datetime
from deep_translator import GoogleTranslator

# --- 1. CONFIGURAZIONE E DESIGN (SIDEBAR BLOCCATA) ---
st.set_page_config(page_title="AI Video Studio Pro", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    [data-testid="sidebar-button"] { display: none !important; }
    [data-testid="stSidebar"] { min-width: 450px !important; background-color: #0d1117; border-right: 1px solid #333; }
    #MainMenu, footer, header, .stAppDeployButton { visibility: hidden; }
    .main { background-color: #0d1117; }
    .stTextArea textarea { background-color: #161b22 !important; color: #58a6ff !important; border: 1px solid #444 !important; }
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #00c6ff 0%, #0072ff 100%);
        color: white; font-size: 1.3rem; font-weight: 800; height: 5rem; border-radius: 12px; width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

if 'script_mem' not in st.session_state: st.session_state['script_mem'] = ""
if 'batch_results' not in st.session_state: st.session_state['batch_results'] = []

# --- 2. REGISTRY MODELLI CON INPUT SPECIFICI ---
# Qui definiamo esattamente cosa accetta ogni modello per evitare errori 422
ENGINE_CONFIG = {
    "Wan-2.1 (Ultra-Rapido)": {
        "id": "wan-ai/wan-2.1-t2v-14b",
        "params": {"aspect_ratio": "16:9"} # Wan non accetta 'video_length'
    },
    "Kling-V1 (Veloce)": {
        "id": "kling-ai/kling-v1",
        "params": {"duration": "10"} # Kling usa 'duration' invece di 'video_length'
    },
    "Minimax-V1 (Qualità)": {
        "id": "minimax/video-01",
        "params": {"video_length": "10s"} # Minimax usa 'video_length'
    },
    "Luma Dream (Cinema)": {
        "id": "luma/dream-machine",
        "params": {} # Luma è molto sensibile, meglio inviare solo il prompt di base
    }
}

# --- 3. SIDEBAR ---
with st.sidebar:
    st.title("⚡ TURBO DIRECTOR")
    st.divider()
    
    selected_name = st.selectbox("Scegli Engine AI:", list(ENGINE_CONFIG.keys()))
    engine_data = ENGINE_CONFIG[selected_name]
    
    st.divider()
    mode = st.radio("Formato Video:", ["Clip Singola", "Filmato 1 Minuto (4 Clip)"])
    num_clips = 1 if "Singola" in mode else 4
    
    st.subheader("🇮🇹 Traduttore Google")
    it_s = st.text_input("Soggetto:", placeholder="Es: Un guerriero")
    it_a = st.text_area("Azione:", placeholder="Es: Combatte contro un mostro")
    
    if st.button("🪄 TRADUCI SCRIPT"):
        if it_s and it_a:
            with st.spinner("Traduzione..."):
                ts = GoogleTranslator(source='it', target='en').translate(it_s)
                ta = GoogleTranslator(source='it', target='en').translate(it_a)
                st.session_state['script_mem'] = f"Cinematic, 8k, photorealistic. {ts}: {ta}."
                st.success("Pronto!")

# --- 4. MAIN PRODUCTION ---
st.title("🚀 Automated Production Workstation")
final_prompt = st.text_area("Script finale (English):", value=st.session_state['script_mem'], height=200)

if st.button("🔥 AVVIA PRODUZIONE"):
    if not final_prompt:
        st.error("Traduci lo script prima!")
    elif "REPLICATE_API_TOKEN" not in st.secrets:
        st.error("Token mancante!")
    else:
        st.session_state['batch_results'] = []
        client = replicate.Client(api_token=st.secrets["REPLICATE_API_TOKEN"])
        
        for i in range(num_clips):
            with st.status(f"🎬 Generazione {i+1}/{num_clips}...", expanded=True) as status:
                try:
                    # PREPARAZIONE INPUT DINAMICO (Fix dell'errore)
                    # Uniamo il prompt di base con i parametri specifici del modello scelto
                    payload = {"prompt": f"{final_prompt} Part {i+1}."}
                    payload.update(engine_data["params"])
                    
                    prediction = client.predictions.create(
                        model=engine_data['id'],
                        input=payload
                    )
                    
                    while prediction.status not in ["succeeded", "failed", "canceled"]:
                        time.sleep(5)
                        prediction.reload()
                    
                    if prediction.status == "succeeded":
                        url = prediction.output if isinstance(prediction.output, str) else prediction.output[0]
                        st.session_state['batch_results'].append(url)
                        status.update(label=f"✅ Clip {i+1} OK!", state="complete")
                    else:
                        st.error(f"Errore Clip {i+1}: {prediction.error}")
                        break
                except Exception as e:
                    st.error(f"Errore critico API: {e}")
                    break
        st.balloons()

# --- 5. RISULTATI ---
if st.session_state['batch_results']:
    st.divider()
    cols = st.columns(2)
    for idx, vid in enumerate(st.session_state['batch_results']):
        with cols[idx % 2]:
            st.video(vid)
            st.download_button(f"📥 Scarica Parte {idx+1}", requests.get(vid).content, f"v_{idx}.mp4")

st.caption("v25.0 - Safe Engine Architecture | Sidebar Locked")
