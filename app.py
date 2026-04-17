"""
================================================================================
AI VIDEO PRODUCTION SUITE - ENTERPRISE EDITION v6.0
--------------------------------------------------------------------------------
DESCRIZIONE: Generatore video multi-engine con gestione avanzata della sessione.
FIX RECENTI: Risolto KeyError su 'timestamp', ottimizzato puntamento modelli 404.
AUTORE: AI Video Studio Team
================================================================================
"""

import streamlit as st
import replicate
import requests
import time
import os
import base64
from datetime import datetime

# ==============================================================================
# 1. CONFIGURAZIONE UI E CSS (SIDEBAR BLOCCATA)
# ==============================================================================

st.set_page_config(
    page_title="AI Video Studio Pro",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS per nascondere menu, footer e bloccare la sidebar
st.markdown("""
    <style>
    /* Blocca la Sidebar: rimuove il tasto di chiusura */
    [data-testid="sidebar-button"] { display: none !important; }
    
    /* Forza larghezza sidebar */
    [data-testid="stSidebar"] {
        min-width: 380px !important;
        max-width: 380px !important;
        border-right: 1px solid #2d2d2d;
    }

    /* Pulizia Interfaccia Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stAppDeployButton {display:none;}
    
    /* Stile personalizzato per i log e i box */
    .status-box {
        padding: 10px;
        border-radius: 5px;
        background-color: #1e2129;
        border-left: 5px solid #ff4b4b;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 2. DEFINIZIONE MODELLI E ENGINE (FIX 404/422)
# ==============================================================================

# Registry dei modelli aggiornato ad Aprile 2026
ENGINE_REGISTRY = {
    "Minimax-V1": {
        "model_id": "minimax/video-01",
        "label": "Il Realista",
        "desc": "Ideale per esseri umani e movimenti naturali. Coerenza facciale elevata.",
        "pros": ["Fotorealismo", "Dettagli 4K", "Fisica accurata"],
        "speed": "2-4 min"
    },
    "Luma-Dream": {
        "model_id": "luma/dream-machine",
        "label": "Il Regista",
        "desc": "Effetti cinematografici e fisica complessa (esplosioni, liquidi).",
        "pros": ["Luci dinamiche", "Movimenti camera pro", "Artistico"],
        "speed": "3-5 min"
    },
    "SVD-Stable": {
        "model_id": "stability-ai/stable-video-diffusion:3f0457d9eddadca94820921444827f0e0103dd90a780bc0642f883f360706222",
        "label": "Lo Scattante",
        "desc": "Il più veloce per brevi loop animati e concept creativi.",
        "pros": ["Velocità", "Costi bassi", "Stile fluido"],
        "speed": "1-2 min"
    }
}

# ==============================================================================
# 3. GESTIONE SESSIONE E STATO (FIX KEYERROR)
# ==============================================================================

def init_session():
    """Inizializza in modo sicuro tutte le variabili di sessione."""
    if 'history' not in st.session_state:
        st.session_state['history'] = []
    if 'counter' not in st.session_state:
        st.session_state['counter'] = 0

init_session()

# ==============================================================================
# 4. SIDEBAR (PANNELLO FISSO CON SPIEGAZIONI)
# ==============================================================================

with st.sidebar:
    st.title("🛡️ AI CONTROL CENTER")
    st.divider()
    
    st.subheader("⚙️ Selezione Engine")
    choice = st.selectbox("Motore di Calcolo:", list(ENGINE_REGISTRY.keys()))
    
    # Visualizzazione info dinamiche Engine
    engine = ENGINE_REGISTRY[choice]
    st.markdown(f"""
    <div class="status-box">
        <strong>{engine['label']}</strong><br>
        <small>{engine['desc']}</small>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("**Vantaggi:**")
    for p in engine['pros']: st.write(f"- {p}")
    st.write(f"⏱️ **Tempo stimato:** {engine['speed']}")
    
    st.divider()
    
    st.subheader("📜 Cronologia Recente")
    if st.session_state['history']:
        # FIX KEYERROR: usiamo .get() per sicurezza
        for i, item in enumerate(reversed(st.session_state['history'][-5:])):
            ts = item.get('timestamp', 'N/D')
            md = item.get('model', 'Sconosciuto')
            st.caption(f"{i+1}. {ts} - {md}")
    else:
        st.caption("Nessun video in questa sessione.")
        
    if st.button("Reset Sessione"):
        st.session_state['history'] = []
        st.rerun()

# ==============================================================================
# 5. UI PRINCIPALE E PROMPT
# ==============================================================================

st.title("🎬 Professional AI Video Production")
st.markdown("---")

col_left, col_right = st.columns([2, 1])

with col_left:
    user_prompt = st.text_area(
        "Descrizione della scena (Prompt):",
        placeholder="A futuristic city in the clouds, cyberpunk style, drone shot...",
        height=200
    )
    
    with st.expander("🛠️ Parametri Avanzati"):
        aspect = st.radio("Formato:", ["16:9", "9:16", "1:1"], horizontal=True)
        safety = st.checkbox("Filtro sicurezza attivo", value=True)

    gen_btn = st.button("🚀 AVVIA GENERAZIONE", use_container_width=True)

with col_right:
    st.subheader("💡 Tips per il successo")
    st.write("1. Usa l'inglese per prompt più precisi.")
    st.write("2. Definisci il movimento della camera.")
    st.write("3. Specifica l'illuminazione (es. 'Neon', 'Sunset').")

# ==============================================================================
# 6. LOGICA DI GENERAZIONE (FIX CRASH)
# ==============================================================================

if gen_btn:
    if not user_prompt:
        st.error("Inserisci una descrizione!")
    elif "REPLICATE_API_TOKEN" not in st.secrets:
        st.error("Token API mancante nei Secrets!")
    else:
        try:
            client = replicate.Client(api_token=st.secrets["REPLICATE_API_TOKEN"])
            target_model = ENGINE_REGISTRY[choice]["model_id"]
            
            with st.status(f"Produzione in corso con {choice}...", expanded=True) as status:
                st.write("📡 Handshake con i server Replicate...")
                
                # Creazione task
                prediction = client.predictions.create(
                    model=target_model,
                    input={"prompt": user_prompt}
                )
                
                # Polling loop
                while prediction.status not in ["succeeded", "failed", "canceled"]:
                    st.write(f"⏳ Elaborazione... ({prediction.status})")
                    time.sleep(10)
                    prediction.reload()
                
                if prediction.status == "succeeded":
                    status.update(label="✅ Video Pronto!", state="complete", expanded=False)
                    res_url = prediction.output if isinstance(prediction.output, str) else prediction.output[0]
                    
                    st.divider()
                    st.video(res_url)
                    
                    # SALVATAGGIO SICURO (Evita KeyError futuri)
                    st.session_state['history'].append({
                        "timestamp": datetime.now().strftime("%H:%M:%S"),
                        "model": choice,
                        "url": res_url
                    })
                    
                    # Download
                    v_data = requests.get(res_url).content
                    st.download_button("📥 Scarica MP4", v_data, f"video_{int(time.time())}.mp4", "video/mp4")
                    st.balloons()
                else:
                    st.error(f"L'AI ha riscontrato un problema: {prediction.error}")
        
        except Exception as e:
            st.error(f"Errore critico: {str(e)}")

# ==============================================================================
# 7. FOOTER TECNICO
# ==============================================================================
st.markdown("---")
st.caption("Enterprise AI Video Suite v6.0 | Dashboard Amministratore | Replicate API Connected")
