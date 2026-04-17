import streamlit as st
import replicate
import os
import requests

# 1. Configurazione Pagina
st.set_page_config(page_title="AI Video Studio", page_icon="🎬")

# 2. Setup Client
if "REPLICATE_API_TOKEN" in st.secrets:
    # Usiamo il token dai segreti di Streamlit
    client = replicate.Client(api_token=st.secrets["REPLICATE_API_TOKEN"])
else:
    st.error("Token non trovato! Inseriscilo nei Secrets di Streamlit Cloud.")
    st.stop()

st.title("🎬 Generatore Video AI Pro")
st.write("Crea video cinematografici con Luma Dream Machine.")

# 3. Form di Input
with st.form("video_form"):
    prompt = st.text_area("Descrizione video:", placeholder="A futuristic car driving through a neon city, cyberpunk style, 4k...")
    aspect_ratio = st.selectbox("Formato:", ["16:9", "9:16", "1:1"])
    submit = st.form_submit_button("Genera Video")

if submit:
    if not prompt:
        st.warning("Inserisci una descrizione!")
    else:
        try:
            with st.spinner("🚀 Luma sta creando il tuo video... (circa 2-3 minuti)"):
                
                # Utilizziamo Luma Dream Machine - Uno dei più stabili su Replicate
                output = client.run(
                    "luma/dream-machine",
                    input={
                        "prompt": prompt,
                        "aspect_ratio": aspect_ratio
                    }
                )

                # Luma restituisce l'URL del video
                video_url = output
                
                st.success("✅ Video Generato!")
                st.video(video_url)
                
                # Download
                video_bytes = requests.get(video_url).content
                st.download_button("💾 Scarica Video", data=video_bytes, file_name="video_ai.mp4")

        except Exception as e:
            st.error(f"Errore: {e}")
            if "402" in str(e) or "free" in str(e).lower():
                st.info("💡 Sembra che i crediti gratuiti siano esauriti. I modelli video richiedono un saldo positivo su Replicate.")
            elif "422" in str(e):
                st.info("💡 Vai su https://replicate.com/luma/dream-machine e clicca 'Run' una volta per accettare i termini del modello.")

st.markdown("---")
st.caption("Creato con Luma + Replicate + Streamlit")
