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
    st.error("⚠️ API Token non trovato! Vai in Settings > Secrets e aggiungi REPLICATE_API_TOKEN.")
    st.stop()

# 3. Interfaccia Utente
st.title("🎬 AI Video Generator")
st.write("Genera brevi video (2-5 secondi) partendo da un'idea testuale.")

with st.form("generator_form"):
    prompt = st.text_area(
        "Descrizione del video (Inglese):",
        placeholder="A rocket launching into space, realistic style, 4k...",
        height=120
    )
    
    submit_button = st.form_submit_button("Genera Video ✨")

# 4. Logica di Esecuzione
if submit_button:
    if not prompt:
        st.warning("Inserisci una descrizione!")
    else:
        try:
            with st.spinner("🚀 Generazione in corso con Stable Video Diffusion..."):
                
                # Utilizziamo un modello ufficiale di Stability AI (molto più stabile)
                # Questo modello genera video partendo da un prompt testuale
                output = client.run(
                    "stability-ai/video-ldm:3f0457d9eddadca94820921444827f0e0103dd90a780bc0642f883f360706222",
                    input={
                        "prompt": prompt,
                        "steps": 25,
                        "fps": 6
                    }
                )

                if output:
                    # Spesso l'output è una lista, prendiamo il primo elemento
                    video_url = output if isinstance(output, str) else output[0]
                    
                    st.success("✅ Video creato con successo!")
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
                    st.error("L'AI non ha restituito alcun file. Riprova.")

        except Exception as e:
            st.error(f"Si è verificato un errore: {e}")
            if "422" in str(e):
                st.info("Questo ID versione è scaduto. Prova a cercare 'Stable Video Diffusion' su Replicate e usa l'ultima versione disponibile.")

st.markdown("---")
st.caption("Powered by Stability AI & Streamlit")
