import streamlit as st
import replicate
import requests
import os
from deep_translator import GoogleTranslator

# ==============================================================================
# 1. DESIGN & CONFIGURAZIONE
# ==============================================================================
st.set_page_config(page_title="Ebook Cover Master v67", page_icon="📚", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0d1117; color: #c9d1d9; }
    [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }
    #MainMenu, footer, header { visibility: hidden; }
    
    /* Input & Selectbox Styling */
    .stTextInput input, .stTextArea textarea, .stSelectbox div {
        background-color: #0d1117 !important;
        color: #58a6ff !important;
        border: 1px solid #30363d !important;
    }

    /* Pulsante Generatore */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #238636 0%, #2ea043 100%);
        color: white; font-size: 1.2rem; font-weight: 800; height: 4rem;
        border-radius: 10px; width: 100%; border: none;
    }
    
    .ebook-preview {
        border-radius: 4px 15px 15px 4px;
        box-shadow: 15px 15px 40px rgba(0,0,0,0.7);
        border-left: 8px solid #222; /* Effetto costa del libro */
    }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 2. SIDEBAR: GENERI AMPLIATI E DATI LIBRO
# ==============================================================================
with st.sidebar:
    st.title("📚 COVER DESIGNER PRO")
    st.caption("v67.0 - Expanded Genres Edition")
    st.divider()
    
    # Lista generi ampliata (ispirata ai migliori tool di scrittura)
    lista_generi = [
        "Narrativa Contemporanea", "Thriller / Noir", "Giallo / Investigativo",
        "Fantasy Epico / High Fantasy", "Urban Fantasy", "Fantascienza / Cyberpunk",
        "Distopico", "Horror / Gotico", "Romanzo Rosa / Romance", 
        "Storico / Historical Fiction", "Avventura", "Young Adult",
        "Saggistica / Self-Help", "Business / Finanza", "Biografia / Memorie",
        "Viaggi / Reportage", "Cucina / Ricettari", "Poesia", "Fiabe per Bambini"
    ]
    
    genre = st.selectbox("Seleziona il Genere:", lista_generi)
    
    title = st.text_input("Titolo dell'Ebook:", placeholder="es. Le Ombre di Marte")
    author = st.text_input("Nome Autore:", placeholder="es. Alessandro Verri")
    
    st.divider()
    desc = st.text_area("Descrizione della Scena (IT):", 
                        placeholder="Descrivi cosa deve apparire (es: Un detective sotto la pioggia in una città futuristica)")
    
    if st.button("🪄 GENERA CONCEPT EDITORIALE"):
        if title and desc:
            with st.spinner("Traduzione e ottimizzazione stile..."):
                t = GoogleTranslator(source='it', target='en')
                scene_en = t.translate(desc)
                
                # Logica di stile per genere
                style_tags = {
                    "Horror / Gotico": "dark, eerie, moody lighting, shadows, atmospheric",
                    "Romanzo Rosa / Romance": "soft colors, ethereal, emotional, pastel tones",
                    "Fantascienza / Cyberpunk": "neon lights, high tech, futuristic, sharp details",
                    "Fantasy Epico / High Fantasy": "magical, painterly style, epic scale, golden hour",
                    "Saggistica / Self-Help": "minimalist, clean typography, bright, professional",
                    "Fiabe per Bambini": "colorful, vibrant, whimsical, illustration style"
                }
                
                tags = style_tags.get(genre, "cinematic, professional composition, high contrast")
                
                st.session_state['p_cover'] = (
                    f"Professional ebook cover for a {genre} book. "
                    f"Visual scene: {scene_en}. Style: {tags}. "
                    f"Typography: The title '{title}' must be clearly integrated into the design with beautiful font. "
                    f"Author: '{author}' written at the bottom. 8k, photorealistic, book cover layout."
                )
                st.success("Concept generato!")

# ==============================================================================
# 3. AREA DI PRODUZIONE
# ==============================================================================
st.title("🎨 Produzione Copertina")
col_l, col_r = st.columns([1.2, 1])

if 'p_cover' not in st.session_state: st.session_state['p_cover'] = ""
if 'cover_url' not in st.session_state: st.session_state['cover_url'] = None

with col_l:
    final_prompt = st.text_area("Prompt Tecnico (EN):", value=st.session_state['p_cover'], height=200)
    
    if st.button("🔥 CREA COPERTINA HD"):
        if not final_prompt:
            st.error("Traduci prima il concept nella sidebar!")
        elif "REPLICATE_API_TOKEN" not in st.secrets:
            st.error("Mancante: REPLICATE_API_TOKEN nei Secrets!")
        else:
            client = replicate.Client(api_token=st.secrets["REPLICATE_API_TOKEN"])
            try:
                with st.spinner("L'IA sta elaborando la grafica..."):
                    # Flux 1.1 Pro è imbattibile per il testo e le copertine
                    output = client.run(
                        "black-forest-labs/flux-1.1-pro",
                        input={
                            "prompt": final_prompt,
                            "aspect_ratio": "2:3",
                            "output_format": "jpg"
                        }
                    )
                    st.session_state['cover_url'] = str(output)
                    st.balloons()
            except Exception as e:
                st.error(f"Errore: {e}")

with col_r:
    st.subheader("🖼️ Anteprima Libro")
    if st.session_state['cover_url']:
        url = st.session_state['cover_url']
        
        # Simulazione visiva di un libro fisico
        st.markdown(f'<img src="{url}" class="ebook-preview" style="width:100%;">', unsafe_allow_html=True)
        
        st.divider()
        st.download_button(
            label="📥 Scarica File per Amazon/Kindle",
            data=requests.get(url).content,
            file_name="copertina_ebook.jpg",
            mime="image/jpeg"
        )
    else:
        st.info("Genera una copertina per vedere l'anteprima 3D.")

st.caption("v67.0 - Ebook Cover Master | Flux 1.1 Pro | Expanded Genre Database")
