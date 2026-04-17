import streamlit as st
import replicate
import requests
import os
from deep_translator import GoogleTranslator

# ==============================================================================
# 1. CONFIGURAZIONE UI
# ==============================================================================
st.set_page_config(page_title="Ebook Designer v74", page_icon="📕", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; min-width: 400px !important; }
    #MainMenu, footer, header { visibility: hidden; }
    .stTextInput input, .stTextArea textarea, .stSelectbox div {
        background-color: #0d1117 !important; color: #58a6ff !important; border: 1px solid #30363d !important;
    }
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #238636 0%, #2ea043 100%);
        color: white; font-size: 1.2rem; font-weight: 800; height: 4rem; border-radius: 10px; border: none;
    }
    .ebook-3d { border-radius: 4px 15px 15px 4px; box-shadow: 20px 20px 50px rgba(0,0,0,0.8); border-left: 10px solid #111; }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 2. DIZIONARIO TRADUZIONI STILI (GENRE MAPPING)
# ==============================================================================
# Qui risolviamo l'errore: ogni scelta IT corrisponde a una descrizione EN professionale
GENRE_STYLES_EN = {
    "Saggio Scientifico": "Modern Academic Science Essay, clean professional layout, minimalist",
    "Quiz Scientifico": "Educational Science Quiz Book, vibrant colors, engaging diagrams",
    "Manuale Tecnico": "Technical Manual, industrial engineering aesthetic, blueprints",
    "Business": "Corporate Business Strategy, luxury gold and navy tones, authoritative",
    "Romanzo Rosa": "Contemporary Romance Novel, soft pastel lighting, emotional atmosphere",
    "Thriller": "Gritty Crime Thriller, high contrast noir, dark mystery vibes",
    "Fantasy": "Epic High Fantasy, magical glow, ornate mystical elements",
    "Fantascienza": "Hard Science Fiction, futuristic cyberpunk HUD, space exploration",
    "Manuale Psicologico": "Self-Help Psychological Guide, serene zen colors, balanced",
    "Biografia": "Historical Biography, classic elegant portraiture, vintage textures"
}

# ==============================================================================
# 3. SIDEBAR
# ==============================================================================
with st.sidebar:
    st.title("📕 DESIGNER v74")
    st.caption("Fix: Genre Translation Matrix")
    st.divider()
    
    # Menu in Italiano
    genre_it = st.selectbox("Categoria Letteraria:", list(GENRE_STYLES_EN.keys()))
    
    st.divider()
    t_text = st.text_input("TITOLO:", placeholder="Scrivi il titolo qui")
    t_pos = st.selectbox("Posizione Titolo:", ["top", "center", "bottom"])
    
    a_text = st.text_input("AUTORE:", placeholder="Nome autore")
    a_pos = st.selectbox("Posizione Autore:", ["top", "center", "bottom"], index=2)

    st.divider()
    desc_it = st.text_area("Descrizione Scena (IT):")
    
    if st.button("🪄 GENERA ARCHITETTURA"):
        if desc_it and t_text:
            with st.spinner("Traduzione totale in corso..."):
                # 1. Traduciamo la descrizione della scena
                scene_en = GoogleTranslator(source='it', target='en').translate(desc_it)
                
                # 2. Recuperiamo la traduzione dello stile dal nostro dizionario
                style_en = GENRE_STYLES_EN.get(genre_it)
                
                # 3. Assembliamo il prompt (Solo in Inglese)
                prompt = (
                    f"IMAGE TEXT RULES: "
                    f"Print the exact title \"{t_text}\" at the {t_pos}. "
                    f"Print the exact author \"{a_text}\" at the {a_pos}. "
                    f"STYLING: This is a {style_en}. "
                    f"SCENE CONTENT: {scene_en}. "
                    f"CRITICAL: Do not write any other words like '{genre_it}'. "
                    f"Professional 8k ebook cover, cinematic lighting, masterpiece."
                )
                
                st.session_state['v74_prompt'] = prompt
                st.success("Tutto tradotto e pronto!")
        else:
            st.error("Inserisci Titolo e Descrizione!")

# ==============================================================================
# 4. PRODUZIONE
# ==============================================================================
st.title("🎨 Workstation Editoriale")
col_l, col_r = st.columns([1.2, 1])

if 'v74_prompt' not in st.session_state: st.session_state['v74_prompt'] = ""
if 'v74_url' not in st.session_state: st.session_state['v74_url'] = None

with col_l:
    p_area = st.text_area("Prompt Tecnico (EN):", value=st.session_state['v74_prompt'], height=250)
    
    if st.button("🔥 GENERA COPERTINA"):
        if not p_area:
            st.error("Genera il prompt prima!")
        else:
            client = replicate.Client(api_token=st.secrets["REPLICATE_API_TOKEN"])
            try:
                with st.spinner("Rendering Flux 1.1 Pro..."):
                    output = client.run(
                        "black-forest-labs/flux-1.1-pro",
                        input={
                            "prompt": p_area,
                            "aspect_ratio": "2:3",
                            "output_format": "jpg"
                        }
                    )
                    st.session_state['v74_url'] = str(output)
                    st.balloons()
            except Exception as e:
                st.error(f"Errore API: {e}")

with col_r:
    st.subheader("🖼️ Risultato Finale")
    if st.session_state['v74_url']:
        st.image(st.session_state['v74_url'], use_container_width=True, output_format="JPEG")
        st.divider()
        st.download_button("📥 Scarica Copertina", requests.get(st.session_state['v74_url']).content, "cover_v74.jpg")
    else:
        st.info("Configura e genera per vedere l'anteprima.")

st.caption("v74.0 - Full Translation Matrix | Flux 1.1 Pro | No IT leakage")
