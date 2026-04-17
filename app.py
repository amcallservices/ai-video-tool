import streamlit as st
import replicate
import requests
import time
import os
import base64
from datetime import datetime

# ==========================================
# 1. CONFIGURAZIONE PAGINA E STILE CSS
# ==========================================
st.set_page_config(
    page_title="AI Video Studio Pro",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Nascondiamo gli elementi di default di Streamlit per un look pulito
hide_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stAppDeployButton {display:none;}
    [data-testid="stHeader"] {background: rgba(0,0,0,0);}
    .block-container {padding-top: 2rem;}
    </style>
"""
st.markdown(hide_style, unsafe_allow_html=True)

# ==========================================
# 2. FUNZIONI DI UTILITÀ
# ==========================================
def get_video_download_link(video_url, filename):
    """Genera un link di download per il video generato."""
    try:
        response = requests.get(video_url)
        if response.status_code == 200:
            b64 = base64.b64encode(response.content).decode()
            return f'<a href="data:video/mp4;base64,{b64}" download="{filename}" style="text-decoration:none;"><button style="background-color:#ff4b4b; color:white; border:none; padding:10px 20px; border-radius:5px; cursor:pointer;">📥 Scarica Video Finale</button></a>'
    except:
        return "Errore nel caricamento del file di download."

def save_to_history(prompt, url):
    """Salva la sessione corrente nella cronologia locale."""
    if 'history' not in st.session_state:
        st.session_state['history'] = []
    st.session_state['history'].append({
        "time": datetime.now().strftime("%H:%M:%S"),
        "prompt": prompt,
        "url": url
    })

# ==========================================
# 3. GESTIONE AUTENTICAZIONE
# ==========================================
if "REPLICATE_API_TOKEN" in st.secrets:
    REPLICATE_TOKEN = st.secrets["REPLICATE_API_TOKEN"]
    os.environ["REPLICATE_API_TOKEN"] = REPLICATE_TOKEN
    client = replicate.Client(api_token=REPLICATE_TOKEN)
else:
    st.error("🔑 API Token mancante. Configura REPLICATE_API_TOKEN nei Secrets di Streamlit.")
    st.stop()

# ==========================================
# 4. SIDEBAR (PANNELLO DI CONTROLLO)
# ==========================================
with st.sidebar:
    st.title("⚙️ Dashboard")
    st.markdown("---")
    
    st.subheader("Parametri AI")
    model_type = st.selectbox(
        "Motore di Generazione",
        ["Minimax (Veloce)", "Luma Dream Machine", "Stable Video Diffusion"],
        index=0
    )
    
    video_quality = st.select_slider(
        "Risoluzione Target",
        options=["Standard", "HD", "Ultra HD"],
        value="HD"
    )
    
    st.markdown("---")
    st.subheader("📜 Cronologia Sessione")
    if 'history' in st.session_state and st.session_state['history']:
        for item in reversed(st.session_state['history']):
            st.text(f"[{item['time']}]")
            st.caption(item['prompt'][:30] + "...")
    else:
        st.write("Nessun video generato.")

# ==========================================
# 5. AREA PRINCIPALE (UI)
# ==========================================
col1, col2 = st.columns([2, 1])

with col1:
    st.title("🎬 AI Video Studio Pro")
    st.markdown("""
    Benvenuto nel tuo studio cinematografico personale. 
    Inserisci una descrizione dettagliata qui sotto e lascia che l'AI faccia il resto.
    """)

    # Area di testo per il prompt
    user_prompt = st.text_area(
        "Cosa vuoi creare oggi?",
        placeholder="Esempio: Una ripresa aerea di un castello medievale circondato da nuvole al tramonto, stile cinematografico, 4k...",
        height=200
    )

    # Opzioni avanzate
    with st.expander("✨ Ottimizzazione Prompt"):
        enhance = st.checkbox("Migliora automaticamente (aggiunge termini tecnici cinematografici)", value=True)
        negative_prompt = st.text_input("Cosa NON vuoi vedere? (Es: blur, distorted, low quality)")

    generate_btn = st.button("🚀 GENERA VIDEO ORA", use_container_width=True)

with col2:
    st.info("💡 **Consiglio Pro:** Descrivi non solo il soggetto, ma anche il movimento della camera (es: 'Panoramica verso destra' o 'Zoom lento').")
    
    # Box statistiche rapide
    st.metric(label="Modello Attivo", value=model_type.split()[0])
    st.metric(label="Tempo stimato", value="~90-120 sec")

# ==========================================
# 6. LOGICA DI GENERAZIONE
# ==========================================
if generate_btn:
    if not user_prompt:
        st.warning("⚠️ Inserisci una descrizione prima di cliccare su genera.")
    else:
        # Raffinamento prompt
        final_prompt = user_prompt
        if enhance:
            final_prompt += ", high quality, 4k, cinematic lighting, masterpiece, detailed textures, stable motion."

        # Container per il caricamento
        with st.status("🛠️ Elaborazione video in corso...", expanded=True) as status:
            try:
                st.write("📡 Connessione al server Replicate...")
                
                # Selezione del modello in base alla scelta
                model_path = "minimax/video-01"
                if model_type == "Luma Dream Machine":
                    model_path = "luma/dream-machine"
                elif model_type == "Stable Video Diffusion":
                    model_path = "stability-ai/stable-video-diffusion:3f0457d9eddadca94820921444827f0e0103dd90a780bc0642f883f360706222"

                prediction = client.predictions.create(
                    model=model_path,
                    input={"prompt": final_prompt}
                )

                # Loop di Polling per monitorare lo stato
                start_time = time.time()
                while prediction.status not in ["succeeded", "failed", "canceled"]:
                    elapsed = int(time.time() - start_time)
                    st.write(f"⏳ Generazione... {elapsed}s (Stato: {prediction.status})")
                    time.sleep(10)
                    prediction.reload()
                
                if prediction.status == "succeeded":
                    status.update(label="✅ Video Generato con Successo!", state="complete", expanded=False)
                    video_url = prediction.output
                    
                    # Mostra il video
                    st.divider()
                    st.video(video_url)
                    
                    # Salva in cronologia e mostra download
                    save_to_history(user_prompt, video_url)
                    
                    st.markdown(get_video_download_link(video_url, "video_studio_pro.mp4"), unsafe_allow_html=True)
                    st.balloons()
                else:
                    status.update(label="❌ Errore durante la generazione.", state="error")
                    st.error(f"Dettagli errore: {prediction.error}")

            except Exception as e:
                status.update(label="🚨 Errore di sistema.", state="error")
                st.error(f"Errore: {str(e)}")
                if "401" in str(e):
                    st.info("Verifica il tuo API Token nei Secrets.")
                elif "402" in str(e):
                    st.info("Credito esaurito su Replicate. Controlla il piano di fatturazione.")

# ==========================================
# 7. FOOTER TECNICO
# ==========================================
st.markdown("---")
st.caption(f"Powered by {model_type} | Versione App 2.4.1 | {datetime.now().year} © VideoStudio AI")
