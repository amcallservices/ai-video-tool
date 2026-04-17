import streamlit as st
import replicate
import requests
import os
from deep_translator import GoogleTranslator

# ==============================================================================
# 1. CONFIGURAZIONE E STILE
# ==============================================================================
st.set_page_config(page_title="Ebook Designer v69", page_icon="🧪", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0d1117; color: #c9d1d9; }
    [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }
    #MainMenu, footer, header { visibility: hidden; }
    
    .stTextInput input, .stTextArea textarea, .stSelectbox div {
        background-color: #0d1117 !important;
        color: #58a6ff !important;
        border: 1px solid #30363d !important;
    }

    div.stButton > button:first-child {
        background: linear-gradient(135deg, #238636 0%, #2ea043 100%);
        color: white; font-size: 1.2rem; font-weight: 800; height: 4rem;
        border-radius: 10px; width: 100%; border: none;
    }
    
    .ebook-preview {
        border-radius: 4px 15px 15px 4px;
        box-shadow: 20px 20px 50px rgba(0,0,0,0.8);
        border-left: 10px solid #111;
        max-width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 2. SIDEBAR: CATEGORIE PERSONALIZZATE E LAYOUT
# ==============================================================================
with st.sidebar:
    st.title("📚 DESIGNER v69")
    st.caption("Categorie Letterarie Custom")
    st.divider()
    
    # Le tue categorie specifiche
    lista_generi = [
        "Saggio Scientifico", "Quiz Scientifico", "Manuale Tecnico",
        "Business", "Romanzo Rosa", "Thriller", 
        "Fantasy", "Fantascienza", "Manuale Psicologico", "Biografia"
    ]
    genre = st.selectbox("Seleziona Categoria:", lista_generi)
    
    st.divider()
    
    # Logica Testo
    show_title = st.checkbox("Inserisci Titolo", value=True)
    title_text = st.text_input("Titolo:", placeholder="Titolo del libro") if show_title else ""
    title_pos = st.selectbox("Posizione Titolo:", ["In alto", "Al centro", "In basso"]) if show_title else ""

    show_author = st.checkbox("Inserisci Autore", value=True)
    author_text = st.text_input("Autore:", placeholder="Nome autore") if show_author else ""
    author_pos = st.selectbox("Posizione Autore:", ["In alto", "Al centro", "In basso"], index=2) if show_author else ""

    st.divider()
    desc_it = st.text_area("Descrizione Scena (IT):", placeholder="Cosa deve apparire nell'immagine?")
    
    if st.button("🪄 GENERA LAYOUT"):
        if desc_it:
            with st.spinner("Creazione prompt..."):
                t = GoogleTranslator(source='it', target='en')
                scene_en = t.translate(desc_it)
                
                text_instructions = []
                if show_title and title_text:
                    text_instructions.append(f"Title '{title_text}' at the {title_pos.replace('In ', '').replace('Al ', '').lower()}.")
                if show_author and author_text:
                    text_instructions.append(f"Author '{author_text}' at the {author_pos.replace('In ', '').replace('Al ', '').lower()}.")
                
                prompt_base = (
                    f"Professional ebook cover for a {genre}. "
                    f"Scene: {scene_en}. "
                    f"{' '.join(text_instructions)} "
                    f"Clean professional typography, cinematic lighting, 8k, photorealistic."
                )
                st.session_state['p_final'] = prompt_base
                st.success("Pronto!")

# ==============================================================================
# 3. WORKSTATION E PREVIEW
# ==============================================================================
st.title("🎨 Produzione Copertine")
col_l, col_r = st.columns([1.2, 1])

if 'p_final' not in st.session_state: st.session_state['p_final'] = ""
if 'res_url' not in st.session_state: st.session_state['res_url'] = None

with col_l:
    p_area = st.text_area("Prompt Tecnico:", value=st.session_state['p_final'], height=200)
    
    if st.button("🔥 GENERA COPERTINA HD"):
        if not p_area:
            st.error("Configura il layout nella sidebar!")
        else:
            client = replicate.Client(api_token=st.secrets["REPLICATE_API_TOKEN"])
            try:
                with st.spinner("Generazione in corso..."):
                    output = client.run(
                        "black-forest-labs/flux-1.1-pro",
                        input={"prompt": p_area, "aspect_ratio": "2:3", "output_format": "jpg"}
                    )
                    st.session_state['res_url'] = str(output)
                    st.balloons()
            except Exception as e:
                st.error(f"Errore: {e}")

with col_r:
    st.subheader("🖼️ Anteprima Risultato")
    if st.session_state['res_url']:
        st.markdown(f'<img src="{st.session_state["res_url"]}" class="ebook-preview">', unsafe_allow_html=True)
        st.divider()
        st.download_button("📥 Scarica Copertina", requests.get(st.session_state['res_url']).content, "cover.jpg", "image/jpeg")
    else:
        st.info("Configura e genera per vedere l'anteprima.")
