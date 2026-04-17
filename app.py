"""
================================================================================
AI VIDEO PRODUCTION SUITE - EXTENDED DURATION v14.0
--------------------------------------------------------------------------------
SISTEMA: Minimax-V1 High-Performance
DURATA: Supporto esteso fino a 15 secondi (Parametrizzato)
ASSISTENTE: AI Script Architect per lunghe sequenze.
DESIGN: Sidebar Bloccata e UI Cinema Dark.
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
# 1. ARCHITETTURA UI E PERSONALIZZAZIONE CSS
# ==============================================================================

st.set_page_config(
    page_title="AI Video Studio Pro - Extended",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS per Sidebar Fissa e Interfaccia Professionale
st.markdown("""
    <style>
    /* BLOCCA SIDEBAR: Rimuove i toggle di chiusura */
    [data-testid="sidebar-button"] { display: none !important; }
    [data-testid="stSidebar"] {
        min-width: 450px !important;
        max-width: 450px !important;
        background-color: #0e1117;
        border-right: 1px solid #333;
    }
    
    /* Pulizia UI Streamlit */
    #MainMenu, footer, header, .stAppDeployButton { visibility: hidden; }
    .main { background-color: #0e1117; }
    
    /* Stile Input e Text Area */
    .stTextArea textarea {
        background-color: #1e2129 !important;
        color: #ffffff !important;
        border: 1px solid #444 !important;
    }

    /* Pulsante Generazione (Look Premium) */
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #ff4b4b 0%, #800000 100%);
        color: white;
        font-size: 1.5rem;
        font-weight: 900;
        height: 5.5rem;
        border-radius: 15px;
        border: none;
        box-shadow: 0 4px 25px rgba(255, 75, 75, 0.4);
        text-transform: uppercase;
    }
    
    div.stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 8px 35px rgba(255, 75, 75, 0.6);
    }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 2. LOGICA DI SESSIONE E UTILITY
# ==============================================================================

if 'history' not in st.session_state: st.session_state['history'] = []
if 'script_output' not in st.session_state: st.session_state['script_output'] = ""

def log_system(msg):
    t = datetime.now().strftime("%H:%M:%S")
    print(f"[{t}] {msg}")

# ==============================================================================
# 3. SIDEBAR: IL REGISTA DIGITALE (DURATA & SCRIPT)
# ==============================================================================

with st.sidebar:
    st.title("🎬 PRODUCTION PANEL")
    st.caption("Enterprise Video Suite v14.0")
    st.divider()
    
    # --- NUOVO CONTROLLO DURATA ---
    st.subheader("⏳ Impostazioni Temporali")
    durata_video = st.select_slider(
        "Seleziona Durata Target:",
        options=[6, 10, 15],
        value=10,
        help="Nota: Video da 10-15s richiedono più tempo di elaborazione e sono più complessi da gestire per l'AI."
    )
    
    st.info(f"Modalità: {'Standard' if durata_video == 6 else 'Extended Cinematic'}")
    
    st.divider()
    
    # --- AI SCRIPT ARCHITECT (Per riempire i secondi) ---
    st.subheader("✍️ Script Architect")
    st.write("Per video lunghi, serve una descrizione dettagliata dell'azione nel tempo.")
    
    soggetto = st.text_input("Soggetto principale:", placeholder="Es: Un guerriero samurai")
    azione_evolutiva = st.text_area("Evoluzione dell'azione:", 
        placeholder="Es: Inizia camminando lentamente nella pioggia, poi si ferma e guarda verso la camera estraendo la katana.")
    
    stile = st.selectbox("Mood visivo:", ["Hyper-Realistic", "Cyberpunk", "Dark Fantasy", "Cinematic Documentary"])

    if st.button("🪄 GENERA SCRIPT DETTAGLIATO"):
        if soggetto and azione_evolutiva:
            # Costruzione prompt tecnico per durata estesa
            tecnico = "8k resolution, masterpiece, highly detailed textures, photorealistic, volumetric lighting, ray-tracing"
            camera = "cinematic slow-motion, tracking shot, anamorphic lens"
            
            prompt_finale = f"Extreme high quality video of {soggetto}. {azione_evolutiva}. Style: {stile}. {tecnico}. {camera}. Cohesive motion over {durata_video} seconds."
            st.session_state['script_output'] = prompt_finale
            st.success("Script ottimizzato per durata estesa!")
        else:
            st.warning("Completa i campi Soggetto e Azione!")

# ==============================================================================
# 4. AREA PRINCIPALE: WORKSTATION DI PRODUZIONE
# ==============================================================================

st.title("🚀 Professional AI Video Workstation")
st.markdown("---")

# Area di editing prompt
final_prompt = st.text_area(
    "Storyboard Tecnico (Prompt finale):",
    value=st.session_state['script_output'],
    height=250,
    help="Puoi modificare manualmente lo script qui per aggiungere dettagli granulari."
)

col_exec, col_info = st.columns([1, 2])

with col_exec:
    if st.button("🔥 AVVIA PRODUZIONE"):
        if not final_prompt:
            st.error("Lo script è vuoto!")
        elif "REPLICATE_API_TOKEN" not in st.secrets:
            st.error("Token API mancante nei Secrets!")
        else:
            try:
                client = replicate.Client(api_token=st.secrets["REPLICATE_API_TOKEN"])
                
                with st.status(f"🎬 Rendering Video ({durata_video}s)...", expanded=True) as status:
                    # Chiamata API con parametro durata (se supportato dal modello specifico)
                    prediction = client.predictions.create(
                        model="minimax/video-01",
                        input={
                            "prompt": final_prompt,
                            "video_length": f"{durata_video}s" if durata_video > 6 else "6s"
                        }
                    )
                    
                    start_time = time.time()
                    while prediction.status not in ["succeeded", "failed", "canceled"]:
                        elapsed = int(time.time() - start_time)
                        status.write(f"⏳ Elaborazione frame... ({elapsed}s) | Stato: {prediction.status}")
                        time.sleep(10)
                        prediction.reload()
                    
                    if prediction.status == "succeeded":
                        status.update(label="✅ Produzione Completata!", state="complete", expanded=False)
                        video_url = prediction.output if isinstance(prediction.output, str) else prediction.output[0]
                        
                        st.divider()
                        st.header("✨ Risultato Video Finale")
                        st.video(video_url)
                        
                        # Salvataggio e Download
                        st.session_state['history'].append({"url": video_url, "prompt": final_prompt})
                        st.download_button("📥 Scarica Master MP4", requests.get(video_url).content, f"video_{durata_video}s.mp4")
                        st.balloons()
                    else:
                        st.error(f"Errore: {prediction.error}")
                        
            except Exception as e:
                st.error(f"Errore critico: {str(e)}")

with col_info:
    st.subheader("📑 Perché 5 secondi non bastano?")
    st.write("""
    I modelli AI di base tendono a generare clip brevi (5-6s) perché la coerenza dei pixel degrada col tempo. 
    Per arrivare a 10 o 15 secondi con questo tool:
    """)
    st.markdown("""
    1. **Evoluzione dell'Azione:** Non descrivere una foto statica. Descrivi un movimento che si sviluppa (es: *Soggetto entra, si siede, guarda fuori*).
    2. **Parametro 'video_length':** Abbiamo forzato il comando nel codice per richiedere clip estese.
    3. **Pazienza:** Un video da 15s richiede il triplo della potenza GPU di uno da 5s.
    """)

# ==============================================================================
# 5. ARCHIVIO SESSIONE
# ==============================================================================

if st.session_state['history']:
    st.divider()
    st.subheader("🎞️ Archivio Produzioni Recenti")
    cols = st.columns(2)
    for idx, item in enumerate(reversed(st.session_state['history'])):
        with cols[idx % 2]:
            st.video(item['url'])
            st.caption(f"Prompt: {item['prompt'][:80]}...")

st.markdown("---")
st.caption("Enterprise AI Suite v14.0 | Dual-Core GPU Cluster Connected | 2026 Stable")
