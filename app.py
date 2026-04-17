import streamlit as st
import replicate
import requests
import time
import os

# 1. Configurazione della Pagina
st.set_page_config(
    page_title="AI Video Studio", 
    page_icon="🎬",
    layout="centered"
)

# 2. Gestione Autenticazione (Secrets)
# Questo blocco legge la chiave REPLICATE_API_TOKEN dai Secrets di Streamlit
if "REPLICATE_API_TOKEN" in st.secrets:
    replicate_token = st.secrets["REPLICATE_API_TOKEN"]
    # Configuriamo l'ambiente per la libreria
    os.environ["REPLICATE_API_TOKEN"] = replicate_token
    client = replicate.Client(api_token=replicate_token)
else:
    st.error("⚠️ Errore: Token non trovato! Configura REPLICATE_API_TOKEN nei Secrets di Streamlit.")
    st.info("Vai su Settings > Secrets e incolla: REPLICATE_API_TOKEN = 'r8_tuotoken'")
    st.stop()

# 3. Interfaccia Utente
st.title("🎬 AI Video Studio")
st.subheader("Trasforma le tue idee in video cinematografici")

with st.form("generator_form"):
    prompt = st.text_area(
        "Descrivi il video (in inglese funziona meglio):",
        placeholder="A futuristic cyber-city with neon lights, flying cars, rain, 4k cinematic style...",
        height=150
    )
    
    # Bottone di invio
    submit_button = st.form_submit_button("Genera Video ✨")

# 4. Logica di Generazione
if submit_button:
    if not prompt:
        st.warning("Per favore, inserisci una descrizione prima di iniziare.")
    else:
        status_placeholder = st.empty()
        
        try:
            status_placeholder.info("🚀 Connessione ai server AI in corso...")
            
            # Creazione della "Prediction" (Processo asincrono)
            # Utilizziamo il modello Minimax che è molto affidabile
            prediction = client.predictions.create(
                model="minimax/video-01",
                input={"prompt": prompt}
            )

            # Loop di controllo dello stato (Polling)
            while prediction.status not in ["succeeded", "failed", "canceled"]:
                status_placeholder.info(f"⏳ L'AI sta creando il video... Stato: {prediction.status}")
                time.sleep(5) # Attendi 5 secondi tra un controllo e l'altro
                prediction.reload() # Aggiorna i dati dal server

            if prediction.status == "succeeded":
                # L'output è l'URL del video generato
                video_url = prediction.output
                status_placeholder.success("✅ Video generato con successo!")
                
                # Visualizzazione Video
                st.video(video_url)
                
                # Bottone per il download locale
                video_content = requests.get(video_url).content
                st.download_button(
                    label="💾 Scarica Video MP4",
                    data=video_content,
                    file_name="video_generato.mp4",
                    mime="video/mp4"
                )
            else:
                st.error(f"La generazione è fallita. Errore: {prediction.error}")

        except Exception as e:
            if "401" in str(e):
                st.error("❌ Errore 401: Autenticazione fallita. Controlla il tuo Token API.")
            elif "402" in str(e) or "free" in str(e).lower():
                st.error("❌ Credito esaurito! I modelli video richiedono un saldo positivo su Replicate.")
            else:
                st.error(f"Si è verificato un errore imprevisto: {e}")

# Footer
st.markdown("---")
st.caption("Creato con Streamlit + Replicate API (Minimax Video-01)")
