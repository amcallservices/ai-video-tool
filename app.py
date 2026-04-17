import streamlit as st
import replicate
import requests
import os
from deep_translator import GoogleTranslator

# ==============================================================================
# 1. CONFIGURAZIONE UI & STYLE
# ==============================================================================
st.set_page_config(page_title="Ebook Designer Pro v75", page_icon="🎨", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; min-width: 420px !important; }
    #MainMenu, footer, header { visibility: hidden; }
    
    /* Input & UI Elements */
    .stTextInput input, .stTextArea textarea, .stSelectbox div {
        background-color: #0d1117 !important; color: #58a6ff !important; border: 1px solid #30363d !important;
    }
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #238636 0%, #2ea043 100%);
        color: white; font-size: 1.2rem; font-weight: 800; height: 4rem; border-radius: 10px; border: none;
    }
    .ebook-3d { 
        border-radius: 4px 15px 15px 4px; 
        box-shadow: 25px 25px 60px rgba(0,0,0,0.8); 
        border-left: 10px solid #111;
        transition: transform 0.3s;
    }
    .ebook-3d:hover { transform: rotateY(-5deg); }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 2. MATRICE DI TRADUZIONE GENERI (FIX ERRORE TRADUZIONE)
# ==============================================================================
GENRE_MAP_EN = {
    "Saggio Scientifico": "Modern Academic Science Essay, professional non-fiction layout",
    "Quiz Scientifico": "Educational Science Quiz Book, vibrant, engaging and dynamic",
    "Manuale Tecnico": "Industrial Technical Manual, engineering blueprints, schematic style",
    "Business": "Corporate Business Strategy, luxury corporate style, authoritative",
    "Romanzo Rosa": "Contemporary Romance Novel, soft pastel lighting, emotional and poetic",
    "Thriller": "Gritty Crime Thriller, high contrast noir lighting, mysterious",
    "Fantasy": "Epic High Fantasy, magical glow, ornate mystical borders",
    "Fantascienza": "Hard Science Fiction, futuristic cyberpunk HUD, space technology",
    "Manuale Psicologico": "Self-Help Psychological Guide, serene zen colors, balanced minimalist",
    "Biografia": "Historical Biography, classic elegant portraiture, vintage paper textures"
}

# ==============================================================================
# 3. SIDEBAR: LOGICA LAYOUT A SCELTA
# ==============================================================================
with st.sidebar:
    st.title("📕 DESIGNER v75")
    st.caption("Custom Layout & Perfect Translation")
    st.divider()
    
    # Selezione Categoria (Tradotta internamente)
    genre_it = st.selectbox("Categoria Letteraria:", list(GENRE_MAP_EN.keys()))
    
    st.divider()
    
    # 1. Scelta Titolo
    use_title = st.checkbox("Inserisci Titolo", value=True)
    if use_title:
        t_val = st.text_input("Testo Titolo:", placeholder="es. L'Atomo Infinito")
        t_pos = st.selectbox("Posizione Titolo:", ["top", "center", "bottom"])
    else:
        t_val, t_pos = None, None

    # 2. Scelta Autore
    use_author = st.checkbox("Inserisci Autore", value=True)
    if use_author:
        a_val = st.text_input("Testo Autore:", placeholder="es. Marco Bianchi")
        a_pos = st.selectbox("Posizione Autore:", ["top", "center", "bottom"], index=2)
    else:
        a_val, a_pos = None, None

    st.divider()
    desc_it = st.text_area("Descrizione Scena (IT):", placeholder="Cosa deve apparire?")
    
    if st.button("🪄 GENERA CONCEPT"):
        if desc_it:
            with st.spinner("Traduzione e analisi layout..."):
                # Traduzione Scena
                scene_en = GoogleTranslator(source='it', target='en').translate(desc_it)
                style_en = GENRE_MAP_EN.get(genre_it)
                
                # Costruzione Regole Testo
                text_rules = []
                if use_title and t_val:
                    text_rules.append(f"Print the main title \"{t_val}\" clearly at the {t_pos} of the cover.")
                if use_author and a_val:
                    text_rules.append(f"Print the author name \"{a_val}\" at the {a_pos} of the cover.")
                
                # Prompt Finale 100% EN
                prompt = (
                    f"IMAGE TEXT RULES: {' '.join(text_rules)} "
                    f"EDITORIAL STYLE: This is a professional {style_en} ebook cover. "
                    f"VISUAL CONTENT: {scene_en}. "
                    f"AUTONOMOUS ELEMENTS: Add editorial subtitle and generic logo icons consistent with the genre. "
                    f"CRITICAL: Do not write the word '{genre_it}' on the image. "
                    f"8k resolution, cinematic lighting, photorealistic, book cover composition."
                )
                
                st.session_state['v75_prompt'] = prompt
                st.success("Concept generato correttamente!")
        else:
            st.error("Inserisci una descrizione visiva!")

# ==============================================================================
# 4. WORKSTATION DI PRODUZIONE
# ==============================================================================
st.title("🎨 Professional Cover Workstation")
col_l, col_r = st.columns([1.2, 1])

if 'v75_prompt' not in st.session_state: st.session_state['v75_prompt'] = ""
if 'v75_res' not in st.session_state: st.session_state['v75_res'] = None

with col_l:
    p_area = st.text_area("Prompt Tecnico (EN):", value=st.session_state['v75_prompt'], height=250)
    
    if st.button("🔥 GENERA COPERTINA HD"):
        if not p_area:
            st.error("Usa la sidebar per generare il prompt!")
        else:
            client = replicate.Client(api_token=st.secrets["REPLICATE_API_TOKEN"])
            try:
                with st.spinner("Rendering Flux 1.1 Pro..."):
                    output = client.run(
                        "black-forest-labs/flux-1.1-pro",
                        input={
                            "prompt": p_area,
                            "aspect_ratio": "2:3",
                            "output_format": "jpg",
                            "output_quality": 100
                        }
                    )
                    st.session_state['v75_res'] = str(output)
                    st.balloons()
            except Exception as e:
                st.error(f"Errore Replicate: {e}")

with col_r:
    st.subheader("🖼️ Risultato Editoriale")
    if st.session_state['v75_res']:
        st.image(st.session_state['v75_res'], use_container_width=True, styling="ebook-3d")
        st.divider()
        st.download_button(
            "📥 Scarica Copertina", 
            requests.get(st.session_state['v75_res']).content, 
            "ebook_cover_v75.jpg"
        )
    else:
        st.info("Configura il layout e clicca su Genera.")

st.caption("v75.0 - Ultimate Fix | Layout a scelta | Traduzione Automatica | Flux 1.1 Pro")
