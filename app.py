import streamlit as st
import replicate
import os
import requests
import time

# 1. Configurazione della pagina (deve essere la prima istruzione Streamlit)
st.set_page_config(
    page_title="AI Video Generator", 
    page_icon="🎥",
    layout="centered"
)

# 2. Gestione dell'autenticazione tramite Secrets
# Assicurati di aver impostato REPLICATE_API_TOKEN nei Secrets di Streamlit Cloud
if "REPLICATE_API_TOKEN" in st.secrets:
    replicate_api_token = st.secrets["REPLICATE_API_TOKEN"]
else:
    st.error("ERRORE: API Token non trovato! Vai in Settings > Secrets e aggiungi REPLICATE_API_TOKEN.")
    st.stop()

# Inizializza il client Replicate
client = replicate.Client(api_token=replicate_api_token)

# 3. Interfaccia Grafica
st.title("🎥 AI Video Studio")
st.markdown("Inserisci una descrizione testuale e l'intelligenza artificiale genererà un video per te.")

# Sidebar per informazioni e parametri
with st.sidebar:
    st.header("Impostazioni")
    durata = st.select_slider(
        "Qualità / Numero Frame",
        options=[41, 81, 121],
        value=81,
        help="Più frame rendono il video più lungo ma la generazione sarà più lenta."
    )
    st.info("Utilizziamo il modello CogVideoX-5b, ottimizzato per velocità e qualità.")

# Form principale
with st.form("my_form"):
    prompt_utente = st.text_area(
        "Cosa vuoi vedere nel video?",
        placeholder="Esempio: Un gatto spaziale che fluttua in una stazione orbitale, stile pixel art, luci neon..."
    )
    
    # Trucco per migliorare il prompt automaticamente
    improve_prompt = st.checkbox("Migliora automaticamente il prompt (aggiunge dettagli cinematografici)", value=True)
    
    submitted = st.form_submit_button("Genera Video")

# 4. Logica di Generazione
if submitted:
    if not prompt_utente:
        st.warning("Per favore, inserisci una descrizione.")
    else:
        try:
            # Raffinamento del prompt
            final_prompt = prompt_utente
            if improve_prompt:
                final_prompt = f"{prompt_utente}, highly detailed, cinematic lighting, 4k resolution, smooth motion, masterpiece."

            with st.spinner("🎬 L'AI sta lavorando... Il video sarà pronto tra circa 60-90 secondi."):
                # Chiamata al modello
                # Modello: CogVideoX-5b (ottimo rapporto qualità/costo)
                output = client.run(
                    "lucataco/cogvideox-5b:096504958319f35315570072b0c3603d1c4728511d739c3629471f28b2488737",
                    input={
                        "prompt": final_prompt,
                        "num_frames": durata,
                        "fps": 8,
                        "guidance_scale": 6
                    }
                )

                # Gestione dell'output (solitamente è un URL diretto)
                video_url = output if isinstance(output, str) else output[0]

                # Visualizzazione del risultato
                st.success("✨ Video generato!")
                st.video(video_url)

                # Download button
                video_bytes = requests.get(video_url).content
                st.download_button(
                    label="⬇️ Scarica il video",
                    data=video_bytes,
                    file_name="video_ai_generato.mp4",
                    mime="video/mp4"
                )

        except Exception as e:
            st.error(f"Si è verificato un errore: {str(e)}")
            st.info("Suggerimento: Controlla che il tuo account Replicate abbia credito sufficiente.")

# Footer
st.markdown("---")
st.caption("Creato con Streamlit + Replicate API")
