import streamlit as st
import replicate
import requests
import time

# 1. Configurazione Pagina
st.set_page_config(page_title="AI Video Studio", page_icon="🎬")

# 2. Setup Client Protetto
if "REPLICATE_API_TOKEN" in st.secrets:
    client = replicate.Client(api_token=st.secrets["REPLICATE_API_TOKEN"])
else:
    st.error("Token non trovato nei Secrets di Streamlit!")
    st.stop()

st.title("🎬 AI Video Studio Pro")

with st.form("video_form"):
    prompt = st.text_area("Cosa vuoi creare?", placeholder="Un'auto futuristica sfreccia in una città neon...")
    submit = st.form_submit_button("Genera Video")

if submit:
    if not prompt:
        st.warning("Inserisci una descrizione!")
    else:
        # Creiamo un contenitore vuoto per i messaggi di stato
        status_container = st.empty()
        
        try:
            status_container.info("⏳ Richiesta inviata ai server... (Fase 1/3)")
            
            # Tentativo di generazione con Luma Dream Machine
            # Usiamo la versione con l'ID più recente e stabile per evitare ambiguità
            prediction = client.predictions.create(
                version="a719512991a10688019446d3e75e95a9b718991f8936631b09b555818ca91e9f", # Luma Dream Machine v1
                input={"prompt": prompt}
            )

            # Fase di monitoraggio (Poling)
            # Invece di client.run, usiamo un loop per evitare timeout del server
            while prediction.status not in ["succeeded", "failed", "canceled"]:
                status_container.info(f"🎬 L'AI sta lavorando... Stato attuale: {prediction.status}")
                time.sleep(5) # Attendi 5 secondi prima di ricontrollare
                prediction.reload() # Aggiorna i dati della predizione

            if prediction.status == "succeeded":
                video_url = prediction.output
                status_container.success("✅ Video generato con successo!")
                st.video(video_url)
                
                # Scaricamento
                video_bytes = requests.get(video_url).content
                st.download_button("💾 Scarica Video", data=video_bytes, file_name="video_ai.mp4")
            else:
                st.error(f"La generazione è fallita con stato: {prediction.status}")

        except Exception as e:
            if "500" in str(e):
                st.error("🚨 Errore 500: I server di Replicate sono sovraccarichi.")
                st.info("Riprova tra 30 secondi: è un problema temporaneo della loro infrastruttura.")
            elif "402" in str(e):
                st.error("💸 Credito esaurito su Replicate! Controlla il tuo piano di fatturazione.")
            else:
                st.error(f"Errore imprevisto: {e}")

st.markdown("---")
st.caption("Se l'errore 500 persiste, prova a cambiare leggermente il prompt o attendi qualche minuto.")
