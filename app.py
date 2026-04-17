import streamlit as st
import replicate
import requests
import time

# 1. Configurazione Pagina
st.set_page_config(page_title="AI Video Studio", page_icon="🎬")

# 2. Controllo Token nei Secrets
if "REPLICATE_API_TOKEN" in st.secrets:
    # Configurazione globale del token per la libreria replicate
    replicate.api_key = st.secrets["REPLICATE_API_TOKEN"]
else:
    st.error("Token non trovato! Vai in Settings > Secrets e aggiungi REPLICATE_API_TOKEN")
    st.stop()

st.title("🎬 AI Video Studio")
st.write("Genera video di alta qualità in pochi minuti.")

# 3. Input Utente
with st.form("video_form"):
    prompt = st.text_area("Descrizione del video (in inglese):", 
                         placeholder="A majestic lion walking through a futuristic neon city, 4k, cinematic...")
    submit = st.form_submit_button("Genera Video ✨")

if submit:
    if not prompt:
        st.warning("Per favore, inserisci una descrizione.")
    else:
        status_placeholder = st.empty()
        
        try:
            status_placeholder.info("🚀 Connessione ai server di generazione...")
            
            # Usiamo il modello Minimax (video-01) che è molto stabile
            # Non usiamo la versione specifica per evitare l'errore 422
            prediction = replicate.predictions.create(
                model="minimax/video-01",
                input={"prompt": prompt}
            )

            # Loop di monitoraggio
            while prediction.status not in ["succeeded", "failed", "canceled"]:
                status_placeholder.info(f"⏳ L'AI sta creando il video... Stato: {prediction.status}")
                time.sleep(10) # Aspettiamo 10 secondi tra un controllo e l'altro
                prediction.reload()

            if prediction.status == "succeeded":
                # L'output di Minimax è direttamente l'URL del video
                video_url = prediction.output
                status_placeholder.success("✅ Video completato!")
                st.video(video_url)
                
                # Download
                video_content = requests.get(video_url).content
                st.download_button("💾 Scarica Video MP4", data=video_content, file_name="video_generato.mp4")
            else:
                st.error(f"Errore nella generazione: {prediction.error}")

        except Exception as e:
            if "422" in str(e):
                st.error("Errore 422: Problema di permessi o versione.")
                st.info("👉 Soluzione: Vai su https://replicate.com/minimax/video-01 e clicca 'Run' una volta per accettare i termini d'uso.")
            elif "402" in str(e):
                st.error("Credito insufficiente su Replicate. Carica almeno 5$ per continuare.")
            else:
                st.error(f"Si è verificato un errore: {e}")

st.markdown("---")
st.caption("Tip: Se il video non appare subito, ricarica la pagina tra qualche istante.")
