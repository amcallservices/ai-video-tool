import streamlit as st
import replicate
import os
import requests

# 1. Configurazione della pagina
st.set_page_config(
    page_title="AI Video Studio", 
    page_icon="🎬",
    layout="centered"
)

# 2. Controllo Autenticazione (Secrets di Streamlit Cloud)
if "REPLICATE_API_TOKEN" in st.secrets:
    api_token = st.secrets["REPLICATE_API_TOKEN"]
    # Inizializziamo il client ufficiale
    client = replicate.Client(api_token=api_token)
else:
    st.error("⚠️ API Token non configurato! Vai in Settings > Secrets e aggiungi REPLICATE_API_TOKEN.")
    st.stop()

# 3. Interfaccia Utente
st.title("🎬 AI Video Generator")
st.write("Inserisci una descrizione e l'AI creerà un video di pochi secondi per te.")

with st.sidebar:
    st.header("Opzioni Modello")
    # Ho impostato il modello CogVideoX che è molto potente e bilanciato
    model_choice = st.selectbox(
        "Scegli il motore AI:",
        ["lucataco/cogvideox-5b", "stability-ai/stable-video-diffusion"]
    )
    st.info("Nota: La generazione richiede solitamente da 1 a 3 minuti.")

# Form di input
with st.form("generator_form"):
    prompt = st.text_area(
        "Descrizione del video (in inglese funziona meglio):",
        placeholder="A majestic dragon flying over a snowy mountain range, cinematic style, 4k...",
        height=120
    )
    
    submit_button = st.form_submit_button("Genera Video ✨")

# 4. Logica di Esecuzione
if submit_button:
    if not prompt:
        st.warning("Scrivi qualcosa prima di generare!")
    else:
        try:
            with st.spinner("🚀 L'AI sta elaborando il video... Prendi un caffè, quasi fatto!"):
                
                # Chiamata API dinamica in base al modello scelto
                if model_choice == "lucataco/cogvideox-5b":
                    output = client.run(
                        model_choice,
                        input={
                            "prompt": prompt,
                            "num_frames": 81,
                            "fps": 8,
                            "guidance_scale": 6
                        }
                    )
                else:
                    # Configurazione per Stable Video Diffusion
                    output = client.run(
                        "stability-ai/stable-video-diffusion:3f0457d9eddadca94820921444827f0e0103dd90a780bc0642f883f360706222",
                        input={"video_length": "14_frames_with_svd"}
                    )

                # Recupero URL del video
                video_url = output if isinstance(output, str) else output[0]

                # Visualizzazione Risultato
                st.success("✅ Generazione completata!")
                st.video(video_url)

                # Bottone di Download
                video_data = requests.get(video_url).content
                st.download_button(
                    label="💾 Scarica Video",
                    data=video_data,
                    file_name="video_generato.mp4",
                    mime="video/mp4"
                )

        except Exception as e:
            # Gestione errori specifica per i permessi/versioni
            if "422" in str(e):
                st.error("Errore 422: Il modello scelto non è al momento disponibile o richiede l'accettazione dei termini su Replicate.com.")
            elif "401" in str(e):
                st.error("Errore 401: Il tuo API Token non è valido. Ricontrolla i Secrets.")
            else:
                st.error(f"Si è verificato un errore inaspettato: {e}")

# Footer
st.markdown("---")
st.caption("Creato con Streamlit & Replicate API")
