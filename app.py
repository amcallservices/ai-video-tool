import streamlit as st
import replicate
import requests
import time
import os
import base64
from datetime import datetime

# ==========================================
# 1. CONFIGURAZIONE PAGINA (SIDEBAR SEMPRE APERTA)
# ==========================================
st.set_page_config(
    page_title="AI Video Studio Pro",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"  # Forza l'apertura all'avvio
)

# --- CSS AVANZATO PER BLOCCARE LA SIDEBAR E PULIRE L'INTERFACCIA ---
style_fix = """
    <style>
    /* Nasconde il pulsante per chiudere la sidebar */
    [data-testid="sidebar-button"] {
        display: none !important;
    }
    
    /* Impedisce alla sidebar di essere trascinata o chiusa su mobile */
    [data-testid="stSidebar"] {
        min-width: 300px !important;
        max-width: 300px !important;
    }

    /* Nasconde i menu standard di Streamlit (Header, Footer, Menu) */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stAppDeployButton {display:none;}
    
    /* Rimuove lo spazio bianco in alto */
    .block-container {
        padding-top: 2rem;
    }
    </style>
"""
st.markdown(style_fix, unsafe_allow_html=True)

# ==========================================
# 2. GESTIONE AUTENTICAZIONE
# ==========================================
if "REPLICATE_API_TOKEN" in st.secrets:
    REPLICATE_TOKEN = st.secrets["REPLICATE_API_TOKEN"]
    os.environ["REPLICATE_API_TOKEN"] = REPLICATE_TOKEN
    client = replicate.Client(api_token=REPLICATE_TOKEN)
else:
    st.error("🔑 API Token mancante nei Secrets di Streamlit.")
    st.stop()

# ==========================================
# 3. SIDEBAR (FISSA E SEMPRE VISIBILE)
# ==========================================
with st.sidebar:
    st.title("⚙️ Pannello Controllo")
    st.divider()
    
    st.subheader("Configurazione AI")
    model_type = st.radio(
        "Seleziona Motore:",
        ["Minimax (Consigliato)", "Luma Dream Machine", "Stable Video Diffusion"]
    )
    
    st.info("💡 La sidebar è fissa per garantire l'accesso rapido ai parametri durante la generazione.")
    
    st.divider()
    st.subheader("📜 Cronologia")
    if 'history' not in st.session_state:
        st.session_state['history'] = []
    
    if st.session_state['history']:
        for item in reversed(st.session_state['history']):
            st.caption(f"🕒 {item['time']} - {item['prompt'][:20]}...")
    else:
        st.write("Nessuna attività.")

# ==========================================
# 4. AREA PRINCIPALE (UI)
# ==========================================
st.title("🎬 AI Video Studio Pro")

col_main, col_info = st.columns([2, 1])

with col_main:
    user_prompt = st.text_area(
        "Descrivi il video che vuoi creare:",
        placeholder="Esempio: Un'aurora boreale sopra una foresta di cristallo, stile fantasy, 8k...",
        height=200
    )
    
    generate_btn = st.button("🚀 GENERA VIDEO", use_container_width=True)

with col_info:
    st.markdown("### 📝 Guida Rapida")
    st.write("1. Scegli il modello a sinistra.")
    st.write("2. Descrivi l'azione e lo stile.")
    st.write("3. Attendi l'elaborazione (90-120s).")

# ==========================================
# 5. LOGICA DI GENERAZIONE
# ==========================================
if generate_btn:
    if not user_prompt:
        st.warning("Inserisci un prompt!")
    else:
        with st.status("🛠️ Generazione in corso...", expanded=True) as status:
            try:
                # Scelta modello
                m_path = "minimax/video-01"
                if "Luma" in model_type: m_path = "luma/dream-machine"
                elif "Stable" in model_type: m_path = "stability-ai/stable-video-diffusion:3f0457d9eddadca94820921444827f0e0103dd90a780bc0642f883f360706222"

                prediction = client.predictions.create(model=m_path, input={"prompt": user_prompt})

                while prediction.status not in ["succeeded", "failed", "canceled"]:
                    st.write(f"⏳ Stato: {prediction.status}...")
                    time.sleep(10)
                    prediction.reload()
                
                if prediction.status == "succeeded":
                    status.update(label="✅ Completato!", state="complete")
                    video_url = prediction.output
                    st.video(video_url)
                    
                    # Salva in cronologia
                    st.session_state['history'].append({
                        "time": datetime.now().strftime("%H:%M"),
                        "prompt": user_prompt
                    })
                    
                    # Bottone download
                    content = requests.get(video_url).content
                    st.download_button("📥 Scarica MP4", content, "video.mp4", "video/mp4")
                else:
                    st.error("Errore durante la creazione.")
            except Exception as e:
                st.error(f"Errore: {e}")

st.markdown("---")
st.caption("© 2026 AI Video Studio - Interfaccia Professionale")
