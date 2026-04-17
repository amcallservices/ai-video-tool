import streamlit as st
import replicate
import requests
import time
import os
from datetime import datetime

# ==========================================
# 1. CONFIGURAZIONE PAGINA E CSS
# ==========================================
st.set_page_config(
    page_title="AI Video Studio Pro",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS per bloccare la sidebar e pulire l'interfaccia
st.markdown("""
    <style>
    [data-testid="sidebar-button"] { display: none !important; }
    [data-testid="stSidebar"] { min-width: 350px !important; max-width: 350px !important; border-right: 1px solid #333; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stAppDeployButton {display:none;}
    .block-container { padding-top: 1rem; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. GESTIONE AUTENTICAZIONE
# ==========================================
if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]
    client = replicate.Client(api_token=st.secrets["REPLICATE_API_TOKEN"])
else:
    st.error("🔑 API Token mancante nei Secrets di Streamlit.")
    st.stop()

# ==========================================
# 3. SIDEBAR (LOGICA E SPIEGAZIONI)
# ==========================================
with st.sidebar:
    st.title("⚙️ CONFIGURAZIONE")
    st.divider()
    
    selected_model = st.radio(
        "Seleziona AI Engine:",
        ["Minimax-V1", "Luma-Dream", "SVD-Stable"],
        help="Scegli il motore in base alle tue esigenze di qualità e velocità."
    )
    
    st.divider()
    st.markdown("### 🧬 Guida agli Engine:")
    
    if selected_model == "Minimax-V1":
        st.info("**Minimax-V1**: Il miglior compromesso. Eccelle nel realismo umano e nella coerenza dei volti. È il più affidabile per video con persone.")
    elif selected_model == "Luma-Dream":
        st.info("**Luma-Dream**: Alta qualità cinematografica. Gestisce movimenti di camera complessi e leggi fisiche (acqua, fuoco) in modo magistrale.")
    else:
        st.info("**SVD-Stable**: Il più veloce. Ottimo per animazioni brevi e creative, ma meno fotorealistico rispetto ai giganti Minimax e Luma.")

    st.divider()
    if 'history' not in st.session_state: st.session_state['history'] = []
    st.metric("Video Generati", len(st.session_state['history']))

# ==========================================
# 4. AREA PRINCIPALE (UI)
# ==========================================
st.title("🎬 AI Video Production Studio")

prompt = st.text_area(
    "Descrizione del video (Storyscript):", 
    placeholder="Esempio: Cinematic drone shot of a volcanic eruption at night, lava flowing into the ocean, 8k...", 
    height=150
)

col_gen, col_empty = st.columns([1, 2])
with col_gen:
    generate_btn = st.button("🚀 AVVIA PRODUZIONE", use_container_width=True)

# ==========================================
# 5. LOGICA DI GENERAZIONE (FIX ERRORE 422/404)
# ==========================================
if generate_btn:
    if not prompt:
        st.warning("⚠️ Inserisci una descrizione!")
    else:
        try:
            # Mappatura corretta per evitare errori di versione
            # Usiamo il formato owner/model che Replicate preferisce
            model_paths = {
                "Minimax-V1": "minimax/video-01",
                "Luma-Dream": "luma/dream-machine",
                "SVD-Stable": "stability-ai/stable-video-diffusion"
            }
            
            target_model = model_paths[selected_model]
            
            with st.status(f"Generazione con {selected_model} in corso...", expanded=True) as status:
                st.write("📡 Invio prompt ai server...")
                
                # Creazione predizione senza ID versione fisso
                prediction = client.predictions.create(
                    model=target_model,
                    input={"prompt": prompt}
                )

                while prediction.status not in ["succeeded", "failed", "canceled"]:
                    st.write(f"⏳ Elaborazione... Stato attuale: {prediction.status}")
                    time.sleep(10)
                    prediction.reload()
                
                if prediction.status == "succeeded":
                    status.update(label="✅ Video Pronto!", state="complete")
                    video_url = prediction.output
                    
                    st.divider()
                    st.video(video_url)
                    
                    # Salvataggio e Download
                    st.session_state['history'].append(video_url)
                    video_bytes = requests.get(video_url).content
                    st.download_button("📥 Scarica Video MP4", video_bytes, "video_ai.mp4", "video/mp4")
                else:
                    st.error(f"Errore nella generazione: {prediction.error}")

        except Exception as e:
            st.error(f"Errore critico: {e}")

st.markdown("---")
st.caption("© 2026 AI Video Studio - Engine: Minimax / Luma / Stability")
