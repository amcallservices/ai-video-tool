"""
================================================================================
AI VIDEO PRODUCTION SUITE - FINAL ENFORCER v33.0
--------------------------------------------------------------------------------
SISTEMA: Minimax-V1 Dedicated
TARGET: Clip Singola Forzata a 15 Secondi
DURATA: Hard-Coded video_length="15s" + FPS=24
TRADUZIONE: Google Translate Bridge (deep-translator)
DESIGN: Sidebar Bloccata (CSS), Workstation Pro
================================================================================
"""

import streamlit as st
import replicate
import requests
import time
from deep_translator import GoogleTranslator

# ==============================================================================
# 1. ARCHITETTURA UI E DESIGN SYSTEM
# ==============================================================================

st.set_page_config(page_title="Minimax 15s Enforcer", page_icon="🎬", layout="wide")

st.markdown("""
    <style>
    /* BLOCCA SIDEBAR */
    [data-testid="sidebar-button"] { display: none !important; }
    [data-testid="stSidebar"] {
        min-width: 400px !important;
        background-color: #0d1117;
        border-right: 1px solid #333;
    }
    #MainMenu, footer, header, .stAppDeployButton { visibility: hidden; }
    .main { background-color: #0d1117; }
    
    /* Input Style Terminal */
    .stTextArea textarea {
        background-color: #161b22 !important;
        color: #58a6ff !important;
        border: 1px solid #30363d !important;
        font-family: 'SF Mono', monospace;
    }

    /* Pulsante Produzione */
    div.stButton > button:first-child {
        background: linear-gradient(180deg, #ff4b4b 0%, #8b0000 100%);
        color: white; font-size: 1.3rem; font-weight: 900; height: 5rem;
        border-radius: 10px; text-transform: uppercase; width: 100%;
        box-shadow: 0 4px 15px rgba(255, 75, 75, 0.3);
    }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 2. LOGICA DI STATO E TRADUZIONE
# ==============================================================================

if 'script_final' not in st.session_state: st.session_state['script_final'] = ""
if 'video_result' not in st.session_state: st.session_state['video_result'] = None

def translate_pro(text):
    if not text: return ""
    try:
        return GoogleTranslator(source='it', target='en').translate(text)
    except:
        return text

# ==============================================================================
# 3. SIDEBAR: CONTROL CENTER
# ==============================================================================

with st.sidebar:
    st.title("🛡️ 15S ENFORCER")
    st.caption("Minimax Dedicated v33.0")
    st.divider()
    
    st.success("MODALITÀ: Clip Singola (15 Secondi Forzati)")
    
    st.subheader("🇮🇹 Storyboard Italiano")
    it_sub = st.text_input("Soggetto:", placeholder="Es: Un guerriero")
    it_act = st.text_area("Azione Dettagliata:", placeholder="Es: Cammina lentamente in una foresta magica")
    
    if st.button("🪄 GENERA SCRIPT TECNICO"):
        if it_sub and it_act:
            with st.spinner("Traduzione in corso..."):
                eng_s = translate_pro(it_sub)
                eng_a = translate_pro(it_act)
                # FORZATURA TEMPORALE NEL PROMPT
                st.session_state['script_final'] = (
                    f"A high-quality 15-second cinematic video. Subject: {eng_s}. "
                    f"Action: {eng_a}. The movement must be extremely slow and continuous "
                    f"for the entire 15 seconds duration. Masterpiece, 8k, photorealistic, "
                    f"detailed textures, volumetric lighting. No still images, full motion."
                )
                st.success("Script da 15s pronto!")
        else:
            st.warning("Compila i campi!")

    st.divider()
    if st.button("Reset"):
        st.session_state.clear()
        st.rerun()

# ==============================================================================
# 4. AREA PRODUZIONE
# ==============================================================================

st.title("🚀 Workstation Produzione 15 Secondi")
st.markdown("---")

col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("📝 Script Tecnico (English)")
    final_p = st.text_area("Verifica Script:", value=st.session_state['script_final'], height=200)
    
    if st.button("🔥 AVVIA RENDERING (FORCE 15s)"):
        if not final_p:
            st.error("Traduci lo script prima!")
        elif "REPLICATE_API_TOKEN" not in st.secrets:
            st.error("Token API mancante!")
        else:
            try:
                client = replicate.Client(api_token=st.secrets["REPLICATE_API_TOKEN"])
                with st.status("🎬 Generazione Video (Locked at 15s)...", expanded=True) as status:
                    # CHIAMATA API CON PARAMETRI HARD-LOCKED
                    prediction = client.predictions.create(
                        model="minimax/video-01",
                        input={
                            "prompt": final_p,
                            "video_length": "15s", # Comando forzato per Minimax
                            "fps": 24              # Standard cinematografico
                        }
                    )
                    
                    while prediction.status not in ["succeeded", "failed", "canceled"]:
                        time.sleep(10)
                        prediction.reload()
                    
                    if prediction.status == "succeeded":
                        url = prediction.output if isinstance(prediction.output, str) else prediction.output[0]
                        st.session_state['video_result'] = url
                        status.update(label="✅ Rendering 15s Completato!", state="complete")
                    else:
                        st.error(f"Errore: {prediction.error}")
            except Exception as e:
                st.error(f"Errore critico: {e}")

with col_right:
    st.subheader("🎞️ Risultato Finale")
    if st.session_state['video_result']:
        st.video(st.session_state['video_result'])
        st.download_button("📥 Scarica Master 15s", requests.get(st.session_state['video_result']).content, "video_15s.mp4")
    else:
        st.info("Il video apparirà qui dopo il rendering.")

st.caption("v33.0 - Final Enforcer | Minimax Dedicated | Sidebar Locked")
