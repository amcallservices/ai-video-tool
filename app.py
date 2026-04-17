"""
================================================================================
AI MULTIMEDIA STUDIO - SINGLE SHOT v64.0
--------------------------------------------------------------------------------
ENGINE VIDEO: Minimax (video-01) - Clip singola da 5 secondi.
COSTO: 1€ per ogni generazione video.
ENGINE IMMAGINE: Flux Schnell (Incluso).
================================================================================
"""

import streamlit as st
import replicate
import requests
import time
import os
from deep_translator import GoogleTranslator

# --- 1. SETUP UI & DESIGN ---
st.set_page_config(page_title="AI Studio 5s", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    /* Blocco Sidebar e Design UI */
    [data-testid="sidebar-button"] { display: none !important; }
    [data-testid="stSidebar"] { min-width: 350px !important; background-color: #0d1117; border-right: 1px solid #333; }
    #MainMenu, footer, header, .stAppDeployButton { visibility: hidden; }
    .main { background-color: #0d1117; color: #c9d1d9; }
    
    /* Box Costo */
    .cost-box {
        background-color: #1e293b;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #3b82f6;
        text-align: center;
        margin-bottom: 20px;
    }

    /* Pulsante Generazione */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #ef4444 0%, #b91c1c 100%);
        color: white; font-size: 1.2rem; font-weight: 800; height: 4rem; border-radius: 10px; width: 100%; border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SESSION STATE ---
if 'p_en' not in st.session_state: st.session_state['p_en'] = ""
if 'media_res' not in st.session_state: st.session_state['media_res'] = None

# --- 3. SIDEBAR ---
with st.sidebar:
    st.title("🎬 STUDIO 5 SECONDI")
    
    st.markdown("""<div class="cost-box">
        <h3 style='margin:0; color:#60a5fa;'>💰 COSTO PRODUZIONE</h3>
        <p style='font-size:1.5rem; font-weight:bold; margin:5px 0;'>1.00 € / Video</p>
        <small style='color:#94a3b8;'>Prezzo stimato per clip da 5s</small>
    </div>""", unsafe_allow_html=True)

    mode = st.radio("Seleziona Formato:", ["Video (5s)", "Immagine HD"])
    st.divider()
    
    it_sub = st.text_input("Soggetto (IT):")
    it_act = st.text_area("Azione (IT):")
    
    if st.button("🪄 TRADUCI SCRIPT"):
        if it_sub and it_act:
            with st.spinner("Traduzione..."):
                t = GoogleTranslator(source='it', target='en')
                st.session_state['p_en'] = f"{t.translate(it_sub)}, {t.translate(it_act)}, cinematic 4k, ultra-realistic."
                st.success("Testo Pronto!")

# --- 4. AREA PRODUZIONE ---
st.title(f"🚀 Workstation: {mode}")
col_l, col_r = st.columns([1.5, 1])

with col_l:
    p_final = st.text_area("Prompt Tecnico (EN):", value=st.session_state['p_en'], height=150)
    
    if st.button("🔥 GENERA ORA"):
        if not p_final:
            st.error("Traduci lo script prima!")
        elif "REPLICATE_API_TOKEN" not in st.secrets:
            st.error("Token API mancante nei Secrets!")
        else:
            client = replicate.Client(api_token=st.secrets["REPLICATE_API_TOKEN"])
            st.session_state['media_res'] = None
            
            try:
                if mode == "Immagine HD":
                    with st.spinner("Creazione Immagine (Flux)..."):
                        out = client.run("black-forest-labs/flux-schnell", input={"prompt": p_final})
                        st.session_state['media_res'] = str(out[0])
                else:
                    with st.status("🎬 Generazione Video 5s (Minimax)...", expanded=True) as status:
                        # Generazione singola clip 5 secondi
                        prediction = client.run(
                            "minimax/video-01",
                            input={"prompt": p_final}
                        )
                        # Minimax restituisce l'URL del video
                        st.session_state['media_res'] = str(prediction)
                        st.balloons()
            
            except Exception as e:
                st.error(f"Errore Replicate: {e}")
                st.info("Assicurati di avere almeno 1€ di credito sul tuo account.")

with col_r:
    st.subheader("🎞️ Anteprima")
    res = st.session_state['media_res']
    if res:
        if mode == "Immagine HD":
            st.image(res)
            st.link_button("📥 Scarica Immagine", res)
        else:
            st.video(res)
            st.link_button("📥 Scarica Video 5s", res)
    else:
        st.info("In attesa di produzione...")

st.caption("v64.0 - Single Shot | Minimax Engine | Costo 1€/Video | Sidebar Locked")
