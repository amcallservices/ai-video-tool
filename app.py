"""
================================================================================
AI VIDEO PRODUCTION SUITE - AUTO-SEQUENCE v22.0
--------------------------------------------------------------------------------
SISTEMA: Minimax-V1 Sequential Engine
LOGICA: Auto-Splitting (1 Minuto = 4x15s)
TRADUZIONE: Google Translate Deep Bridge
DESIGN: Sidebar Bloccata, Cinema UI
================================================================================
"""

import streamlit as st
import replicate
import requests
import time
import os
from deep_translator import GoogleTranslator

# --- CONFIGURAZIONE UI ---
st.set_page_config(page_title="AI Video Studio - Auto-Sequence", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    [data-testid="sidebar-button"] { display: none !important; }
    [data-testid="stSidebar"] { min-width: 450px !important; background-color: #0d1117; border-right: 1px solid #333; }
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
        color: white; font-size: 1.3rem; font-weight: 800; height: 5rem;
        border-radius: 10px; border: none; text-transform: uppercase; width: 100%;
        box-shadow: 0 4px 15px rgba(255, 75, 75, 0.3);
    }
    </style>
    """, unsafe_allow_html=True)

# --- MOTORE TRADUZIONE ---
def translate_it(text):
    if not text: return ""
    try:
        return GoogleTranslator(source='it', target='en').translate(text)
    except:
        return text

# --- SESSION STATE ---
if 'batch_clips' not in st.session_state: st.session_state['batch_clips'] = []
if 'is_generating' not in st.session_state: st.session_state['is_generating'] = False

# --- SIDEBAR ---
with st.sidebar:
    st.title("🎬 AUTO-SEQUENCE ENGINE")
    st.write("Configura la tua produzione cinematografica lunga.")
    
    st.divider()
    
    target_duration = st.selectbox("Durata Totale Video:", ["15 Secondi (Clip singola)", "1 Minuto (4 Clip automatiche)"])
    num_clips = 1 if "15" in target_duration else 4
    
    st.subheader("🇮🇹 Input Storyboard")
    it_sog = st.text_input("Soggetto (Chi/Cosa):", placeholder="Es: Un astronauta su Marte")
    it_azi = st.text_area("Azione Evolutiva:", 
                         placeholder="Descrivi cosa succede nell'arco del tempo (es: Inizia a camminare, poi trova un cristallo, lo analizza e infine corre via)")
    
    st.info(f"Il sistema genererà {num_clips} clip da 15s ciascuna.")

# --- MAIN WORKSTATION ---
st.title("🚀 Automated Video Production Line")
st.markdown("---")

col_left, col_right = st.columns([2, 1])

with col_left:
    if st.button("🔥 AVVIA PRODUZIONE AUTOMATIZZATA"):
        if not it_sog or not it_azi:
            st.error("Inserisci soggetto e azione per iniziare.")
        elif "REPLICATE_API_TOKEN" not in st.secrets:
            st.error("Token API mancante nei Secrets!")
        else:
            st.session_state['is_generating'] = True
            st.session_state['batch_clips'] = []
            
            # Traduzione una tantum del soggetto
            eng_sog = translate_it(it_sog)
            eng_azi_full = translate_it(it_azi)
            
            # Blueprint tecnico
            blueprint = "Cinematic 8k, masterpiece, highly detailed, 35mm, golden hour, smooth motion."
            
            client = replicate.Client(api_token=st.secrets["REPLICATE_API_TOKEN"])
            
            # Ciclo di generazione automatica
            for i in range(num_clips):
                step_label = f"Clip {i+1} di {num_clips}"
                with st.status(f"🎬 Elaborazione {step_label}...", expanded=True) as status:
                    
                    # Prompt differenziato per clip (aggiunge 'part X' per coerenza)
                    final_p = f"{blueprint} Subject: {eng_sog}. Action: {eng_azi_full}. Sequence part {i+1}. Continuous motion 15s."
                    
                    prediction = client.predictions.create(
                        model="minimax/video-01",
                        input={"prompt": final_p, "video_length": "15s"}
                    )
                    
                    while prediction.status not in ["succeeded", "failed", "canceled"]:
                        time.sleep(10)
                        prediction.reload()
                    
                    if prediction.status == "succeeded":
                        url = prediction.output if isinstance(prediction.output, str) else prediction.output[0]
                        st.session_state['batch_clips'].append({"url": url, "prompt": final_p})
                        status.update(label=f"✅ {step_label} Completata!", state="complete")
                    else:
                        st.error(f"Errore nella {step_label}: {prediction.error}")
                        break
            
            st.session_state['is_generating'] = False
            st.balloons()

with col_right:
    st.subheader("📦 Risultati Batch")
    if st.session_state['batch_clips']:
        for idx, clip in enumerate(st.session_state['batch_clips']):
            st.write(f"**Clip {idx+1}**")
            st.video(clip['url'])
            st.download_button(f"📥 Scarica Clip {idx+1}", requests.get(clip['url']).content, f"video_part_{idx+1}.mp4")
    else:
        st.write("Nessun video in coda. Avvia la produzione per vedere i risultati.")

# Istruzioni post-produzione
if len(st.session_state['batch_clips']) == 4:
    st.success("🎯 Tutte le clip per il video di 1 minuto sono pronte! Scaricale e uniscile in ordine.")
