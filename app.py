"""
================================================================================
PROGETTO: AI VIDEO STUDIO ENTERPRISE v5.0
DESCRIZIONE: Suite professionale per la generazione video tramite API Replicate.
LOGICA: Gestione dinamica dei modelli, Polling asincrono e UI Personalizzata.
DOCUMENTAZIONE: https://replicate.com/docs/reference/http#predictions.create
================================================================================
"""

import streamlit as st
import replicate
import requests
import time
import os
import base64
import logging
from datetime import datetime
from PIL import Image
from io import BytesIO

# ==============================================================================
# 1. CONFIGURAZIONE E ARCHITETTURA DELLA PAGINA
# ==============================================================================

# Impostiamo il layout 'wide' per massimizzare lo spazio visivo del video.
# La sidebar viene impostata come espansa di default tramite configurazione Streamlit.
st.set_page_config(
    page_title="AI Video Studio Pro - Enterprise Edition",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Definiamo i percorsi dei modelli aggiornati (Fix per errore 404)
# Per SVD usiamo la versione stabile verificata per evitare errori di puntamento.
MODEL_REGISTRY = {
    "Minimax-V1": {
        "path": "minimax/video-01",
        "tagline": "Coerenza fotorealistica superiore",
        "use_case": "Video con esseri umani, interviste AI, scene d'azione fluide.",
        "specs": "Risoluzione: 1280x720 | Durata: 6s | Qualità: Alta"
    },
    "Luma-Dream": {
        "path": "luma/dream-machine",
        "tagline": "Cinematografia e fisica avanzata",
        "use_case": "Paesaggi, effetti speciali, movimenti di camera complessi.",
        "specs": "Risoluzione: 1360x752 | Durata: 5s | Qualità: Cinematografica"
    },
    "SVD-Stable": {
        "path": "stability-ai/stable-video-diffusion:3f0457d9eddadca94820921444827f0e0103dd90a780bc0642f883f360706222",
        "tagline": "Rapidità e animazione creativa",
        "use_case": "Loop artistici, sfondi animati, prototipazione rapida.",
        "specs": "Risoluzione: 1024x576 | Durata: 4s | Qualità: Standard"
    }
}

# ==============================================================================
# 2. DESIGN E CUSTOM CSS (SIDEBAR BLOCCATA)
# ==============================================================================

def inject_enterprise_styles():
    """Inietta CSS avanzato per bloccare la sidebar e rimuovere il branding standard."""
    st.markdown("""
        <style>
        /* Blocco Sidebar: Rimuove l'icona di chiusura e forza la visibilità */
        [data-testid="sidebar-button"] {
            display: none !important;
        }
        
        /* Larghezza sidebar fissa per layout professionale */
        [data-testid="stSidebar"] {
            min-width: 400px !important;
            max-width: 400px !important;
            border-right: 1px solid #2d2d2d;
            background-color: #0e1117;
        }

        /* Nasconde header, footer e menu 'Made with Streamlit' */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stAppDeployButton {display:none;}
        
        /* Miglioramento della leggibilità dei testi */
        .stMarkdown p {
            font-size: 1.1rem;
            line-height: 1.6;
        }
        
        /* Stile pulsante Generazione */
        div.stButton > button:first-child {
            background-color: #ff4b4b;
            color: white;
            border: none;
            padding: 20px;
            font-size: 1.2rem;
            font-weight: bold;
            border-radius: 12px;
            transition: 0.3s ease;
            width: 100%;
        }
        
        div.stButton > button:hover {
            background-color: #ff3333;
            transform: scale(1.02);
            box-shadow: 0 4px 15px rgba(255, 75, 75, 0.4);
        }

        /* Container Video Custom */
        .video-container {
            border: 2px solid #333;
            border-radius: 15px;
            overflow: hidden;
            margin-top: 20px;
        }
        </style>
        """, unsafe_allow_html=True)

inject_enterprise_styles()

# ==============================================================================
# 3. LOGICA DI SISTEMA E GESTIONE ERRORI
# ==============================================================================

def initialize_session():
    """Inizializza le variabili di sessione per tracciare attività e cronologia."""
    if 'history' not in st.session_state:
        st.session_state['history'] = []
    if 'total_generated' not in st.session_state:
        st.session_state['total_generated'] = 0
    if 'last_status' not in st.session_state:
        st.session_state['last_status'] = "Pronto all'uso"

def get_api_client():
    """Configura e restituisce il client Replicate verificando le credenziali."""
    if "REPLICATE_API_TOKEN" in st.secrets:
        token = st.secrets["REPLICATE_API_TOKEN"]
        return replicate.Client(api_token=token)
    return None

def download_video(url):
    """Scarica il video dall'URL per permettere il download locale."""
    try:
        response = requests.get(url)
        return response.content
    except Exception as e:
        st.error(f"Errore durante il download del video: {e}")
        return None

# ==============================================================================
# 4. COMPONENTI DELLA SIDEBAR (PANNELLO FISSO)
# ==============================================================================

initialize_session()

with st.sidebar:
    st.title("🛡️ AI CONTROL CENTER")
    st.caption("Piattaforma di Produzione Video Professionale")
    st.divider()
    
    # Selezione del Motore AI (AI Engine Selector)
    st.subheader("⚙️ Configurazione Engine")
    engine_choice = st.selectbox(
        "Seleziona Motore di Calcolo:",
        list(MODEL_REGISTRY.keys()),
        index=0,
        help="Scegli l'engine in base alla necessità di realismo o velocità."
    )
    
    # Spiegazione dettagliata tipologie AI Engine (Richiesta Utente)
    selected_info = MODEL_REGISTRY[engine_choice]
    st.info(f"**{selected_info['tagline']}**\n\n{selected_info['use_case']}")
    st.markdown(f"📊 **Specifiche Tecniche:**\n_{selected_info['specs']}_")
    
    st.divider()
    
    # Dashboard Statistiche
    st.subheader("📈 Session Stats")
    col_stat1, col_stat2 = st.columns(2)
    col_stat1.metric("Video Creati", st.session_state['total_generated'])
    col_stat2.metric("Stato Server", "Online", delta_color="normal")
    
    st.divider()
    
    # Cronologia Rapida
    st.subheader("📜 Recent History")
    if st.session_state['history']:
        for i, item in enumerate(reversed(st.session_state['history'][-5:])):
            st.caption(f"{i+1}. {item['timestamp']} - {item['model']}")
    else:
        st.caption("Nessuna generazione recente.")
        
    if st.button("Pulisci Dati Sessione"):
        st.session_state['history'] = []
        st.session_state['total_generated'] = 0
        st.rerun()

# ==============================================================================
# 5. INTERFACCIA PRINCIPALE E LOGICA DI GENERAZIONE
# ==============================================================================

st.title("🎬 Professional AI Video Studio")
st.markdown("---")

# Area di input per il prompt testuale
col_input, col_info = st.columns([2, 1])

with col_input:
    prompt_text = st.text_area(
        "Inserisci lo Storyboard / Prompt del video:",
        placeholder="Descrivi l'azione, l'atmosfera e i dettagli visivi (in inglese)...",
        height=200,
        help="Esempio: A majestic dragon flying over a snowy peak, cinematic lighting, ultra-detailed."
    )
    
    # Opzioni di ottimizzazione prompt
