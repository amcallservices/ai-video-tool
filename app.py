import streamlit as st
import replicate
import requests
import time
import os
import base64
import json
from datetime import datetime

# ==============================================================================
# CONFIGURAZIONE AVANZATA DELLA PAGINA
# ==============================================================================
# Impostiamo il layout 'wide' per dare respiro al video e la sidebar espansa di default.
st.set_page_config(
    page_title="AI Video Production Suite - Professional Edition",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# CSS INJECTION PER BLOCCARE LA SIDEBAR E PULIRE L'UI
# ==============================================================================
# Questo blocco forza la sidebar a rimanere visibile e nasconde i tasti di chiusura.
st.markdown("""
    <style>
    /* 1. Blocca la sidebar: nasconde il bottone di chiusura (freccia/X) */
    [data-testid="sidebar-button"] {
        display: none !important;
    }
    
    /* 2. Forza la larghezza della sidebar per evitare che sparisca su resize */
    [data-testid="stSidebar"] {
        min-width: 350px !important;
        max-width: 350px !important;
        border-right: 1px solid #464b5d;
    }

    /* 3. Nasconde gli elementi "brandizzati" di Streamlit per un look custom */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stAppDeployButton {display:none;}
    
    /* 4. Estetica generale: font e spaziature */
    .main {
        background-color: #0e1117;
    }
    .stTextArea textarea {
        background-color: #1e2129;
        color: #ffffff;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #ff4b4b;
        color: white;
        font-weight: bold;
        border: none;
    }
    .stButton>button:hover {
        background-color: #ff3333;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# GESTIONE SESSION STATE (MEMORIA DELL'APP)
# ==============================================================================
# Inizializziamo le variabili di memoria per evitare errori di 'KeyError'
if 'history' not in st.session_state:
    st.session_state['history'] = []
if 'logs' not in st.session_state:
    st.session_state['logs'] = [f"{datetime.now().strftime('%H:%M:%S')} - Sistema Inizializzato"]
if 'generation_count' not in st.session_state:
    st.session_state['generation_count'] = 0

def add_log(message):
    """Aggiunge un evento al log di sistema visibile nella sidebar."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state['logs'].append(f"{timestamp} - {message}")

# ==============================================================================
# FUNZIONI CORE: GENERAZIONE E DOWNLOAD
# ==============================================================================
def check_auth():
    """Verifica la presenza del token Replicate nei Secrets."""
    if "REPLICATE_API_TOKEN" in st.secrets:
        os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]
        return replicate.Client(api_token=st.secrets["REPLICATE_API_TOKEN"])
    return None

def process_video_generation(client, prompt, model_alias):
    """Gestisce l'invio e il monitoraggio della generazione video."""
    try:
        # Mappatura dei modelli ai percorsi API ufficiali
        model_map = {
            "Minimax-V1": "minimax/video-01",
            "Luma-Dream": "luma/dream-machine",
            "SVD-Stable": "stability-ai/stable-video-diffusion:3f0457d9eddadca94820921444827f0e0103dd90a780bc0642f883f360706222"
        }
        
        path = model_map.get(model_alias, "minimax/video-01")
        add_log(f"Richiesta inviata al modello: {model_alias}")
        
        # Creazione della predizione
        prediction = client.predictions.create(model=path, input={"prompt": prompt})
        
        # Monitoraggio attivo (Polling)
        with st.status(f"Generazione con {model_alias}...", expanded=True) as status:
            while prediction.status not in ["succeeded", "failed", "canceled"]:
                status.write(f"Stato: {prediction.status}... ({datetime.now().strftime('%H:%M:%S')})")
                time.sleep(8)
                prediction.reload()
            
            if prediction.status == "succeeded":
                status.update(label="Generazione Completata!", state="complete")
                return prediction.output
            else:
                status.update(label="Errore di Generazione", state="error")
                add_log(f"Fallimento: {prediction.error}")
                return None
    except Exception as e:
        st.error(f"Errore critico: {str(e)}")
        add_log(f"Errore API: {str(e)[:50]}")
        return None

# ==============================================================================
# SIDEBAR FISSA (PANNELLO DI CONTROLLO)
# ==============================================================================
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/movie-beginning.png", width=80)
    st.title("Control Panel")
    st.markdown("---")
    
    # Sezione Parametri
    st.header("🛠️ Settings")
    selected_model = st.radio(
        "AI Engine",
        ["Minimax-V1", "Luma-Dream", "SVD-Stable"],
        help="Scegli il motore di intelligenza artificiale per la generazione."
    )
    
    video_duration = st.slider("Target Duration (Sec)", 5, 10, 5)
    
    st.markdown("---")
    
    # Sezione Logs (Debug in tempo reale)
    st.header("📊 System Logs")
    log_box = st.container(height=200)
    for log in reversed(st.session_state['logs']):
        log_box.caption(log)
        
    if st.button("Clear Logs"):
        st.session_state['logs'] = [f"{datetime.now().strftime('%H:%M:%S')} - Logs Puliti"]
        st.rerun()

# ==============================================================================
# AREA PRINCIPALE (USER INTERFACE)
# ==============================================================================
client_instance = check_auth()

if not client_instance:
    st.warning("⚠️ Accesso Negato: Token API non trovato. Configura i Secrets su Streamlit Cloud.")
    st.stop()

# Layout a due colonne per l'area di lavoro
main_col, side_col = st.columns([2, 1])

with main_col:
    st.title("🎬 Professional AI Video Studio")
    st.info("Benvenuto. Inserisci una descrizione testuale dettagliata per iniziare la produzione.")
    
    full_prompt = st.text_area(
        "Video Script / Storyboard Prompt",
        placeholder="Esempio: Cinematic shot of a futuristic city with flying neon cars, heavy rain, 8k resolution...",
        height=250,
        help="Più dettagli inserisci (luci, movimenti camera, stile), migliore sarà il risultato."
    )
    
    # Opzioni aggiuntive (Expandable)
    with st.expander("🎨 Advanced Style Options"):
        c1, c2 = st.columns(2)
        with c1:
            lighting = st.selectbox("Lighting", ["Cinematic", "Natural", "Neon", "Studio", "Dark"])
        with c2:
            camera = st.selectbox("Camera Movement", ["Static", "Slow Zoom", "Pan Left", "Drone Shot", "Handheld"])
        
        style_suffix = f", lighting: {lighting}, camera: {camera}, high quality, detailed."

    generate_trigger = st.button("START GENERATION")

with side_col:
    st.header("📥 Output Area")
    st.write("I tuoi video appariranno qui sotto una volta pronti.")
    
    if st.session_state['history']:
        last_video = st.session_state['history'][-1]
        st.success(f"Ultimo video generato alle {last_video['time']}")
        st.video(last_video['url'])
        
        # Download Button
        try:
            v_data = requests.get(last_video['url']).content
            st.download_button(
                label="Download MP4",
                data=v_data,
                file_name=f"ai_video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4",
                mime="video/mp4"
            )
        except:
            st.error("Impossibile generare il tasto download al momento.")
    else:
        st.info("Nessun video nella coda di questa sessione.")

# ==============================================================================
# LOGICA DI ESECUZIONE AL CLICK
# ==============================================================================
if generate_trigger:
    if not full_prompt:
        st.error("Errore: Il prompt non può essere vuoto.")
        add_log("Errore: Tentativo di generazione con prompt vuoto.")
    else:
        # Combinazione prompt utente + parametri scelti
        final_input = full_prompt + style_suffix
        
        # Avvio processo
        add_log(f"Avvio generazione con input: {full_prompt[:20]}...")
        result_url = process_video_generation(client_instance, final_input, selected_model)
        
        if result_url:
            st.session_state['history'].append({
                "time": datetime.now().strftime("%H:%M:%S"),
                "url": result_url,
                "prompt": full_prompt
            })
            st.session_state['generation_count'] += 1
            add_log("Generazione completata con successo.")
            st.balloons()
            st.rerun()

# ==============================================================================
# CRONOLOGIA IN FONDO ALLA PAGINA
# ==============================================================================
if len(st.session_state['history']) > 1:
    st.markdown("---")
    st.header("🎞️ Session History")
    # Mostriamo una griglia di video passati
    hist_cols = st.columns(3)
    for idx, item in enumerate(reversed(st.session_state['history'][:-1])):
        with hist_cols[idx % 3]:
            st.caption(f"Generato alle: {item['time']}")
            st.video(item['url'])
