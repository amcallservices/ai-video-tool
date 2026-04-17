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

# 2. Controllo Autenticazione
if "REPLICATE_API_TOKEN" in st.secrets:
    api_token = st.secrets["REPLICATE_API_TOKEN"]
    client = replicate.Client(api_token=api_token)
else:
    st.error("⚠️ API Token non configurato nei Secrets di Streamlit!")
    st.stop()

# 3. Interfaccia Utente
st.title("🎬 AI Video Generator")
st.write("Genera video realistici dall'intelligenza artificiale.")

with st.form("generator_form"):
    prompt = st.text_area(
        "Descrizione del video (Inglese consigliato):",
        placeholder="A golden retriever puppy running in a field of sunflowers, 4k, cinematic...",
        height=120
    )
    
    submit_button = st.form_submit_button("Genera Video ✨")

# 4. Logica di Esecuzione
if submit_button:
    if not prompt:
        st.warning("Inserisci una descrizione!")
    else:
        try:
            with st.spinner("🚀 Generazione in corso... (circa 2 minuti)"):
                
                # UTILIZZIAMO L'ID VERSIONE FISSO PER EVITARE IL 404
                # Modello: CogVideoX-5b di lucataco
                model_version = "lucataco/cogvideox-5b:096504958319f35315570072b0c3603d1c4728511d739c3629471f28b2488737"
                
                output = client.run(
                    model_version,
                    input={
                        "prompt": prompt,
                        "num_frames": 81,
                        "fps": 8,
                        "guidance_scale": 6
                    }
                )

                # Gestione dell'output
                if output:
                    video_url = output if isinstance(output, str) else output[0]
                    
                    st.success("✅ Video creato!")
                    st.video(video_url)

                    # Bottone di Download
                    video_data = requests.get(video_url).content
                    st.download_button(
                        label="💾 Scarica Video",
                        data=video_data,
                        file_name="video_ai.mp4",
                        mime="video/mp4"
                    )
                else:
                    st.error("L'AI non ha restituito alcun video. Riprova con un prompt diverso.")

        except Exception as e:
            st.error(f"Si è verificato un errore: {e}")
            if "401" in str(e):
                st.info("Controlla che il tuo Token sia corretto e che tu abbia credito su Replicate.")
            elif "404" in str(e):
                st.info("Il modello è temporaneamente offline o l'ID versione è cambiato.")

st.markdown("---")
st.caption("Powered by Replicate & Streamlit")
