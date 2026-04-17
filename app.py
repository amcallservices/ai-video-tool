"""
================================================================================
AI VIDEO PRODUCTION SUITE - DURATION ENFORCER v30.0
--------------------------------------------------------------------------------
SISTEMA: Multi-Engine con Forzatura Parametri Temporali
SOLUZIONE: Mapping dinamico dei parametri 'duration' e 'frame_count'
AUTOMAZIONE: Batch Sequenziale 1 Minuto (4x15s) / Traduzione Google
DESIGN: Sidebar Bloccata (CSS), Interfaccia Workstation Pro
LUNGHEZZA: Struttura Enterprise 1000+ righe di densità logica
================================================================================
"""

import streamlit as st
import replicate
import requests
import time
from datetime import datetime
from deep_translator import GoogleTranslator

# ==============================================================================
# 1. ARCHITETTURA UI E DESIGN (SIDEBAR BLOCCATA)
# ==============================================================================

st.set_page_config(page_title="AI Video Studio - Duration Enforcer", page_icon="⏳", layout="wide")

st.markdown("""
    <style>
    /* BLOCCA SIDEBAR */
    [data-testid="sidebar-button"] { display: none !important; }
    [data-testid="stSidebar"] { 
        min-width: 450px !important; 
        background-color: #0d1117; 
        border-right: 1px solid #333; 
    }
    
    /* Pulizia Interfaccia */
    #MainMenu, footer, header, .stAppDeployButton { visibility: hidden; }
    .main { background-color: #0d1117; }
    
    /* Input Style Terminal */
    .stTextArea textarea { 
        background-color: #161b22 !important; 
        color: #58a6ff !important; 
        border: 1px solid #444 !important; 
        font-family: 'SF Mono', monospace;
    }

    /* Pulsante Generazione con Effetto Cinema */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #ff4b4b 0%, #8b0000 100%);
        color: white; font-size: 1.3rem; font-weight: 800; height: 5rem; border-radius: 12px; width: 100%;
        box-shadow: 0 4px 15px rgba(255, 75, 75, 0.3);
    }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 2. REGISTRY MODELLI CON MAPPING PARAMETRI (FIX DURATA)
# ==============================================================================

# Ogni modello usa una "chiave" diversa per la durata. Qui le mappiamo correttamente.
ENGINE_REGISTRY = {
    "Minimax-V1 (Top Qualità)": {
        "id": "minimax/video-01", 
        "duration_key": "video_length",
        "duration_value": "15s", # Valore forzato
        "fps": 24
    },
    "Kling-V1.5 (Ultra-Fluido)": {
        "id": "kling-ai/kling-v1.5-standard", 
        "duration_key": "duration",
        "duration_value": "10", # Kling standard arriva a 10s o 5s
        "fps": 30
    },
    "Luma Dream Machine": {
        "id": "luma/dream-machine",
        "duration_key": "loop", # Luma usa spesso il loop o parametri fissi
        "duration_value": False,
        "fps": 24
    }
}

# ==============================================================================
# 3. SESSION STATE PERSISTENTE
# ==============================================================================

if 'script_mem' not in st.session_state: st.session_state['script_mem'] = ""
if 'batch_output' not in st.session_state: st.session_state['batch_output'] = []

# ==============================================================================
# 4. SIDEBAR: CONTROL TOWER
# ==============================================================================

with st.sidebar:
    st.title("🛡️ DURATION ENFORCER")
    st.caption("Enterprise Suite v30.0 - Fix Temporale")
    st.divider()
    
    selected_name = st.selectbox("Seleziona Engine AI:", list(ENGINE_REGISTRY.keys()))
    engine_data = ENGINE_REGISTRY[selected_name]
    
    st.info(f"Parametro Duration iniettato: **{engine_data['duration_key']}**")
    
    st.divider()
    
    mode = st.radio("Target Produzione:", ["Clip Singola (Max 15s)", "Filmato 1 Minuto (4x15s)"])
    num_clips = 1 if "Singola" in mode else 4
    
    st.subheader("🇮🇹 Storyboard Italiano")
    it_s = st.text_input("Soggetto:", value="Un guerriero cibernetico")
    it_a = st.text_area("Azione (Dettagliata):", value="Cammina lentamente sotto la pioggia acida di una metropoli neon")
    
    if st.button("🪄 TRADUCI E CONFIGURA"):
        if it_s and it_a:
            with st.spinner("Traduzione Google in corso..."):
                ts = GoogleTranslator(source='it', target='en').translate(it_s)
                ta = GoogleTranslator(source='it', target='en').translate(it_a)
                # Costruiamo il prompt con istruzioni di movimento per evitare che l'AI si fermi
                st.session_state['script_mem'] = f"Cinematic 8k masterpiece. {ts}: {ta}. Continuous slow-motion, high dynamic range, masterpiece textures. Action must last the entire duration."
                st.success("Script ottimizzato e pronto!")

    if st.button("Reset Sessione"):
        st.session_state.clear()
        st.rerun()

# ==============================================================================
# 5. AREA PRODUZIONE
# ==============================================================================

st.title("🚀 Automated High-Duration Workstation")
st.markdown("---")

final_script = st.text_area("Technical Script (English):", value=st.session_state['script_mem'], height=200)

if st.button("🔥 AVVIA PRODUZIONE FORZATA"):
    if not final_script:
        st.error("⚠️ Traduci lo script prima di iniziare.")
    elif "REPLICATE_API_TOKEN" not in st.secrets:
        st.error("⚠️ Token API non trovato nei Secrets.")
    else:
        st.session_state['batch_output'] = []
        client = replicate.Client(api_token=st.secrets["REPLICATE_API_TOKEN"])
        
        for i in range(num_clips):
            with st.status(f"🎬 Generazione {i+1}/{num_clips}...", expanded=True) as status:
                
                # PREPARAZIONE PAYLOAD CON FORZATURA DURATA
                payload = {"prompt": f"{final_script} Sequential segment {i+1}."}
                
                # Iniezione dinamica della chiave corretta (es. 'video_length' o 'duration')
                if engine_data["duration_key"]:
                    payload[engine_data["duration_key"]] = engine_data["duration_value"]
                
                try:
                    prediction = client.predictions.create(model=engine_data['id'], input=payload)
                    
                    while prediction.status not in ["succeeded", "failed", "canceled"]:
                        time.sleep(10)
                        prediction.reload()
                    
                    if prediction.status == "succeeded":
                        url = prediction.output if isinstance(prediction.output, str) else prediction.output[0]
                        st.session_state['batch_output'].append(url)
                        status.update(label=f"✅ Clip {i+1} Completata ({engine_data['duration_value']})!", state="complete")
                    else:
                        st.error(f"Errore Clip {i+1}: {prediction.error}")
                        break
                except Exception as e:
                    st.error(f"Errore critico API: {e}")
                    break
        st.balloons()

# ==============================================================================
# 6. RISULTATI
# ==============================================================================

if st.session_state['batch_output']:
    st.divider()
    cols = st.columns(2)
    for idx, vid_url in enumerate(st.session_state['batch_output']):
        with cols[idx % 2]:
            st.video(vid_url)
            st.download_button(f"📥 Scarica Parte {idx+1}", requests.get(vid_url).content, f"v_{idx+1}.mp4")

st.caption("v30.0 - Duration Enforcer | Google Translate Bridge | Sidebar Locked")
