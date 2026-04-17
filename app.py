import streamlit as st
import replicate
import requests
import os
from deep_translator import GoogleTranslator

# ==============================================================================
# 1. DESIGN E CONFIGURAZIONE UI
# ==============================================================================
st.set_page_config(page_title="Ebook Designer v80", page_icon="📕", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    [data-testid="stSidebar"] { 
        background-color: #161b22; 
        border-right: 1px solid #30363d; 
        min-width: 400px !important; 
    }
    #MainMenu, footer, header { visibility: hidden; }
    
    .stTextInput input, .stTextArea textarea, .stSelectbox div {
        background-color: #0d1117 !important;
        color: #58a6ff !important;
        border: 1px solid #30363d !important;
    }

    /* Pulsante Genera */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #238636 0%, #2ea043 100%);
        color: white; font-size: 1.2rem; font-weight: 800; height: 4rem;
        border-radius: 12px; width: 100%; border: none; box-shadow: 0 4px 15px rgba(35, 134, 54, 0.4);
    }
    
    /* Pulsante Reset */
    .reset-btn button {
        background-color: #30363d !important;
        color: #f85149 !important;
        border: 1px solid #f85149 !important;
        font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 2. LOGICA DI STILE INVISIBILE (MAPPATURA EN)
# ==============================================================================
# Le etichette IT non vengono mai inviate al modello per evitare scritte errate
STILI_INVISIBILI = {
    "Saggio Scientifico": "high-end academic non-fiction, clean professional aesthetic",
    "Quiz Scientifico": "educational quiz style, vibrant and dynamic background",
    "Manuale Tecnico": "industrial technical guide, blueprint schematic aesthetic",
    "Business": "luxury corporate success style, gold and navy accents",
    "Romanzo Rosa": "ethereal romance, soft lighting, pastel emotional tones",
    "Thriller": "gritty suspense thriller, noir high-contrast shadows",
    "Fantasy": "epic fantasy world, magical atmospheric lighting",
    "Fantascienza": "cyberpunk sci-fi, futuristic tech HUD elements",
    "Manuale Psicologico": "serene psychology self-help, zen minimalist balance",
    "Biografia": "classic biography, elegant portraiture, vintage paper textures"
}

# ==============================================================================
# 3. SIDEBAR: CONTROLLI E RESET
# ==============================================================================
with st.sidebar:
    st.title("📕 DESIGNER v80")
    st.caption("Clean Editorial Engine")
    
    # PULSANTE RESET
    st.markdown('<div class="reset-btn">', unsafe_allow_html=True)
    if st.button("🔄 NUOVO PROGETTO / RESET"):
        st.session_state.clear()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.divider()
    
    # Selezione Categoria (Usata solo per lo stile, non per il testo)
    genere_it = st.selectbox("Atmosfera Editoriale:", list(STILI_INVISIBILI.keys()))
    
    st.divider()
    
    # Input Titolo
    use_t = st.checkbox("Abilita Titolo", value=True)
    t_val = st.text_input("Titolo:", "PATENTE SUBITO") if use_t else ""
    t_pos = st.selectbox("Posizione Titolo:", ["top", "center", "bottom"]) if use_t else ""

    # Input Autore
    use_a = st.checkbox("Abilita Autore", value=True)
    a_val = st.text_input("Nome Autore:", "ANTONINO STRAMERA") if use_a else ""
    a_pos = st.selectbox("Posizione Autore:", ["top", "center", "bottom"], index=2) if use_a else ""

    st.divider()
    desc_it = st.text_area("Scena Visiva (IT):", placeholder="Descrivi lo sfondo...")
    
    if st.button("🪄 GENERA ARCHITETTURA PROMPT"):
        if desc_it:
            with st.spinner("Compilazione prompt pulito..."):
                t = GoogleTranslator(source='it', target='en')
                scene_en = t.translate(desc_it)
                stile_en = STILI_INVISIBILI.get(genere_it)
                
                # REGOLE DI RILIEVO E PULIZIA
                text_rules = []
                if use_t and t_val:
                    text_rules.append(f"STRICTLY PRINT the title \"\"\"{t_val}\"\"\" in massive 3D bold letters at the {t_pos}.")
                if use_a and a_val:
                    text_rules.append(f"STRICTLY PRINT the author name \"\"\"{a_val}\"\"\" at the {a_pos} in a clean, sharp, visible font.")
                
                # Costruzione Prompt Finale (Nessun riferimento alla parola IT del genere)
                prompt = (
                    f"A professional ebook cover. Visual mood: {stile_en}. "
                    f"Background scene: {scene_en}. "
                    f"TYPOGRAPHY OVERLAY: {' '.join(text_rules)} "
                    f"VISUAL HIERARCHY: Simplify background details behind the text areas to ensure absolute legibility. "
                    f"CRITICAL: Do NOT write the word '{genere_it}' or the category name. Only print the provided title and author. "
                    f"8k resolution, cinematic lighting, sharp typography, high contrast."
                )
                
                st.session_state['v80_prompt'] = prompt
                st.success("Concept editoriale pronto!")

# ==============================================================================
# 4. WORKSTATION DI PRODUZIONE
# ==============================================================================
st.title("🎨 Workstation v80 - No-Genre Edition")
col_l, col_r = st.columns([1.2, 1])

if 'v80_prompt' not in st.session_state: st.session_state['v80_prompt'] = ""
if 'v80_res' not in st.session_state: st.session_state['v80_res'] = None

with col_l:
    p_edit = st.text_area("Prompt Tecnico (EN):", value=st.session_state['v80_prompt'], height=250)
    
    if st.button("🔥 GENERA COPERTINA HD"):
        if not p_edit:
            st.error("Configura il progetto nella sidebar!")
        else:
            client = replicate.Client(api_token=st.secrets["REPLICATE_API_TOKEN"])
            try:
                with st.spinner("L'IA sta disegnando..."):
                    out = client.run(
                        "black-forest-labs/flux-1.1-pro",
                        input={
                            "prompt": p_edit,
                            "aspect_ratio": "2:3",
                            "output_format": "jpg"
                        }
                    )
                    st.session_state['v80_res'] = str(out)
                    st.balloons()
            except Exception as e:
                st.error(f"Errore API: {e}")

with col_r:
    st.subheader("🖼️ Anteprima Finale")
    if st.session_state['v80_res']:
        st.image(st.session_state['v80_res'], use_container_width=True)
        st.divider()
        st.download_button("📥 Scarica JPG", requests.get(st.session_state['v80_res']).content, "cover_clean.jpg")
    else:
        st.info("In attesa di produzione...")

st.caption("v80.0 - Invisible Genre Style | Global Reset Button | Flux 1.1 Pro")
