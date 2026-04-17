import streamlit as st
import replicate
import requests
import os
from deep_translator import GoogleTranslator

# ==============================================================================
# 1. CONFIGURAZIONE E STILE
# ==============================================================================
st.set_page_config(page_title="Ebook Designer Pro v68", page_icon="🎨", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0d1117; color: #c9d1d9; }
    [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }
    #MainMenu, footer, header { visibility: hidden; }
    
    /* Input Styling */
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
        box-shadow: 20px 20px 50px rgba(0,0,0,0.8);
        border-left: 10px solid #111;
        max-width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 2. SIDEBAR: LOGICA DI POSIZIONAMENTO TESTO
# ==============================================================================
with st.sidebar:
    st.title("📚 DESIGNER v68")
    st.caption("Personalizza Layout e Testo")
    st.divider()
    
    # 1. Scelta Genere
    lista_generi = [
        "Thriller / Noir", "Fantasy Epico", "Sci-Fi / Cyberpunk",
        "Romanzo Rosa", "Horror / Gotico", "Saggistica / Business", 
        "Storico", "Giallo", "Fiabe per Bambini"
    ]
    genre = st.selectbox("Genere:", lista_generi)
    
    st.divider()
    
    # 2. Logica Titolo
    show_title = st.checkbox("Inserisci Titolo", value=True)
    if show_title:
        title_text = st.text_input("Titolo:", placeholder="Titolo del libro")
        title_pos = st.selectbox("Posizione Titolo:", ["In alto", "Al centro", "In basso"], index=0)
    else:
        title_text = ""
        title_pos = ""

    # 3. Logica Autore
    show_author = st.checkbox("Inserisci Nome Autore", value=True)
    if show_author:
        author_text = st.text_input("Autore:", placeholder="Nome dell'autore")
        author_pos = st.selectbox("Posizione Autore:", ["In alto", "Al centro", "In basso"], index=2)
    else:
        author_text = ""
        author_pos = ""

    st.divider()
    desc_it = st.text_area("Descrizione Scena (IT):", placeholder="Cosa deve apparire nell'immagine?")
    
    if st.button("🪄 GENERA LAYOUT"):
        if desc_it:
            with st.spinner("Creazione prompt grafico..."):
                t = GoogleTranslator(source='it', target='en')
                scene_en = t.translate(desc_it)
                
                # Costruzione istruzioni testuali
                text_instructions = []
                if show_title and title_text:
                    text_instructions.append(f"The title '{title_text}' written in large, stylish font at the {title_pos.replace('In ', '').replace('Al ', '').lower()} of the cover.")
                if show_author and author_text:
                    text_instructions.append(f"The author name '{author_text}' written in elegant font at the {author_pos.replace('In ', '').replace('Al ', '').lower()} of the cover.")
                
                prompt_base = (
                    f"A professional ebook cover for a {genre} book. "
                    f"Main scene: {scene_en}. "
                    f"{' '.join(text_instructions)} "
                    f"High quality graphic design, cinematic lighting, 8k, photorealistic."
                )
                st.session_state['p_final'] = prompt_base
                st.success("Layout pronto!")

# ==============================================================================
# 3. AREA PRODUZIONE
# ==============================================================================
st.title("🎨 Workstation Creativa")
col_l, col_r = st.columns([1.2, 1])

if 'p_final' not in st.session_state: st.session_state['p_final'] = ""
if 'res_url' not in st.session_state: st.session_state['res_url'] = None

with col_l:
    p_area = st.text_area("Prompt Finale (Modificabile):", value=st.session_state['p_final'], height=200)
    
    if st.button("🔥 GENERA COPERTINA"):
        if not p_area:
            st.error("Configura il layout nella sidebar!")
        elif "REPLICATE_API_TOKEN" not in st.secrets:
            st.error("Manca il Token API!")
        else:
            client = replicate.Client(api_token=st.secrets["REPLICATE_API_TOKEN"])
            try:
                with st.spinner("Generazione in corso (Flux Pro)..."):
                    output = client.run(
                        "black-forest-labs/flux-1.1-pro",
                        input={
                            "prompt": p_area,
                            "aspect_ratio": "2:3",
                            "output_format": "jpg"
                        }
                    )
                    st.session_state['res_url'] = str(output)
                    st.balloons()
            except Exception as e:
                st.error(f"Errore: {e}")

with col_r:
    st.subheader("🖼️ Risultato Finale")
    if st.session_state['res_url']:
        st.markdown(f'<img src="{st.session_state["res_url"]}" class="ebook-preview">', unsafe_allow_html=True)
        st.divider()
        st.download_button(
            label="📥 Scarica Copertina HD",
            data=requests.get(st.session_state['res_url']).content,
            file_name="cover_ebook.jpg",
            mime="image/jpeg"
        )
    else:
        st.info("Configura il titolo e la posizione per iniziare.")

st.caption("v68.0 - Custom Layout Edition | Flux 1.1 Pro Engine")
