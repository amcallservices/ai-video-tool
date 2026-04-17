import streamlit as st
import replicate
import requests
import time
import os
from PIL import Image
from io import BytesIO
from deep_translator import GoogleTranslator

# ==============================================================================
# 1. DESIGN & LAYOUT (EBOOK EDITION)
# ==============================================================================
st.set_page_config(page_title="Ebook Cover Designer", page_icon="📚", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0f172a; color: #f1f5f9; }
    [data-testid="stSidebar"] { background-color: #1e293b; border-right: 1px solid #334155; }
    #MainMenu, footer, header { visibility: hidden; }
    
    /* Input Styling */
    .stTextInput input, .stTextArea textarea, .stSelectbox div {
        background-color: #0f172a !important;
        color: #38bdf8 !important;
        border: 1px solid #334155 !important;
    }

    /* Pulsante Gold */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #fbbf24 0%, #d97706 100%);
        color: #000; font-size: 1.2rem; font-weight: 800; height: 4rem;
        border-radius: 12px; width: 100%; border: none; box-shadow: 0 4px 20px rgba(217, 119, 6, 0.4);
    }
    
    /* Preview Ebook */
    .ebook-preview {
        border: 10px solid #1e293b;
        border-radius: 5px;
        box-shadow: 20px 20px 60px #080c14, -20px -20px 60px #16223e;
    }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 2. SIDEBAR: PARAMETRI EDITORIALI
# ==============================================================================
with st.sidebar:
    st.title("📚 COVER MASTER")
    st.caption("AI Design for Ebooks & Kindle")
    st.divider()
    
    genre = st.selectbox("Genere Letterario:", [
        "Thriller / Mistero", "Fantasy / Epico", "Fantascienza / Sci-Fi", 
        "Romanzo Rosa", "Saggistica / Business", "Horror", "Manuale Tecnico"
    ])
    
    title = st.text_input("Titolo dell'Ebook:", placeholder="es. L'Ultima Frontiera")
    author = st.text_input("Nome Autore:", placeholder="es. Mario Rossi")
    
    st.divider()
    desc = st.text_area("Descrizione della scena:", placeholder="es. Una foresta innevata con un lupo solitario sotto la luna piena")
    
    aspect_ratio = "2:3" # Formato standard ebook
    
    if st.button("🪄 GENERA CONCEPT"):
        if title and desc:
            with st.spinner("Ottimizzazione prompt..."):
                t = GoogleTranslator(source='it', target='en')
                scene_en = t.translate(desc)
                title_en = title.upper()
                
                # Prompt Engineering specifico per copertine
                # Flux è eccellente nel rendere il testo se specificato tra virgolette
                st.session_state['cover_prompt'] = (
                    f"Professional ebook cover for a {genre} book. "
                    f"Central visual: {scene_en}. "
                    f"The image should have the title '{title}' written in elegant, readable typography at the top. "
                    f"The author name '{author}' should be at the bottom. "
                    f"Cinematic lighting, high contrast, book cover composition, award-winning design, 8k."
                )
                st.success("Design pronto per la generazione!")

# ==============================================================================
# 3. WORKSTATION DI GENERAZIONE
# ==============================================================================
st.title("🎨 Editor Copertina Ebook")
col_l, col_r = st.columns([1, 1])

if 'cover_prompt' not in st.session_state: st.session_state['cover_prompt'] = ""
if 'final_image' not in st.session_state: st.session_state['final_image'] = None

with col_l:
    final_p = st.text_area("Prompt Tecnico per l'IA:", value=st.session_state['cover_prompt'], height=200)
    
    if st.button("🔥 GENERA COPERTINA HD"):
        if not final_p:
            st.error("Traduci il concept prima!")
        elif "REPLICATE_API_TOKEN" not in st.secrets:
            st.error("Manca il Token API!")
        else:
            client = replicate.Client(api_token=st.secrets["REPLICATE_API_TOKEN"])
            try:
                with st.spinner("L'IA sta disegnando la tua copertina..."):
                    # Usiamo Flux.1 Pro per la massima leggibilità del testo
                    output = client.run(
                        "black-forest-labs/flux-1.1-pro",
                        input={
                            "prompt": final_p,
                            "aspect_ratio": "2:3",
                            "output_format": "jpg",
                            "output_quality": 100
                        }
                    )
                    st.session_state['final_image'] = str(output)
                    st.balloons()
            except Exception as e:
                st.error(f"Errore: {e}")

# ==============================================================================
# 4. ANTEPRIMA PROFESSIONALE
# ==============================================================================
with col_r:
    st.subheader("🖼️ Anteprima Editoriale")
    if st.session_state['final_image']:
        img_url = st.session_state['final_image']
        
        # Visualizzazione con stile "Libro"
        st.markdown(f'<img src="{img_url}" class="ebook-preview" style="width:100%;">', unsafe_allow_html=True)
        
        st.markdown("---")
        st.download_button(
            label="📥 Scarica Copertina (Alta Risoluzione)",
            data=requests.get(img_url).content,
            file_name="ebook_cover.jpg",
            mime="image/jpeg"
        )
    else:
        st.info("Riempi i campi a sinistra e genera per vedere l'anteprima.")

st.caption("v66.0 - Ebook Cover Master | Flux Pro Engine | Formato 2:3")
