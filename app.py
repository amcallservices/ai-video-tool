import streamlit as st
import replicate
import requests
import time
import os

# 1. SETUP E CSS (Invariato per mantenere la sidebar fissa)
st.set_page_config(page_title="AI Video Studio Pro", page_icon="🎬", layout="wide", initial_sidebar_state="expanded")
st.markdown("<style>[data-testid='sidebar-button'] { display: none !important; } [data-testid='stSidebar'] { min-width: 350px !important; } #MainMenu, footer, header {visibility: hidden;}</style>", unsafe_allow_html=True)

# 2. AUTENTICAZIONE
if "REPLICATE_API_TOKEN" in st.secrets:
    client = replicate.Client(api_token=st.secrets["REPLICATE_API_TOKEN"])
else:
    st.error("Token mancante nei Secrets!")
    st.stop()

# 3. SIDEBAR CON SPIEGAZIONI ENGINE
with st.sidebar:
    st.title("⚙️ ENGINE AI")
    selected_model = st.radio("Scegli il motore:", ["Minimax-V1", "Luma-Dream", "SVD-Stable"])
    st.divider()
    
    # Spiegazione delle tipologie per il cliente
    if selected_model == "Minimax-V1":
        st.write("✨ **Il Realista**: Eccelle nei volti umani e movimenti fluidi. È il più moderno.")
    elif selected_model == "Luma-Dream":
        st.write("🎥 **Il Regista**: Grandi effetti cinematografici e fisica accurata (fuoco, acqua).")
    else:
        st.write("⚡ **Lo Scattante**: Più veloce, ideale per brevi clip artistiche e astratte.")

# 4. UI PRINCIPALE
st.title("🎬 AI Video Production Studio")
prompt = st.text_area("Descrizione video:", placeholder="A futuristic car racing in a neon city...", height=150)
generate_btn = st.button("🚀 AVVIA PRODUZIONE", use_container_width=True)

# 5. LOGICA DI GENERAZIONE (VERSIONI AGGIORNATE PER EVITARE 404)
if generate_btn:
    if not prompt:
        st.warning("Inserisci un prompt!")
    else:
        try:
            # Mappatura con VERSIONI FISSE (Le più stabili ad oggi)
            model_configs = {
                "Minimax-V1": "minimax/video-01", 
                "Luma-Dream": "luma/dream-machine",
                "SVD-Stable": "stability-ai/stable-video-diffusion:3f0457d9eddadca94820921444827f0e0103dd90a780bc0642f883f360706222"
            }
            
            target = model_configs[selected_model]
            
            with st.status(f"Generazione con {selected_model}...", expanded=True) as status:
                # Per Minimax e Luma usiamo il deploy senza versione se possibile, 
                # per SVD forziamo la versione che sappiamo esistere.
                prediction = client.predictions.create(
                    model=target,
                    input={"prompt": prompt}
                )

                while prediction.status not in ["succeeded", "failed", "canceled"]:
                    st.write(f"⏳ Stato: {prediction.status}...")
                    time.sleep(10)
                    prediction.reload()
                
                if prediction.status == "succeeded":
                    video_url = prediction.output
                    st.video(video_url)
                    st.success("✅ Video completato!")
                    
                    # Tasto Download
                    data = requests.get(video_url).content
                    st.download_button("📥 Scarica MP4", data, "video_ai.mp4", "video/mp4")
                else:
                    st.error(f"Errore Replicate: {prediction.error}")

        except Exception as e:
            st.error(f"Errore critico: {e}")
            st.info("Se l'errore è 404, il modello potrebbe aver cambiato indirizzo API. Prova un altro Engine.")
