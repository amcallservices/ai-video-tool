import streamlit as st
import replicate
import requests
import os
from deep_translator import GoogleTranslator

# ==============================================================================
# 1. CONFIGURAZIONE E DESIGN
# ==============================================================================
st.set_page_config(page_title="Ebook Designer v82", page_icon="📕", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; min-width: 400px !important; }
    header, footer, .stAppDeployButton { display: none !important; }
    
    .stTextInput input, .stTextArea textarea, .stSelectbox div {
        background-color: #0d1117 !important; color: #58a6ff !important; border: 1px solid #30363d !important;
    }
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #238636 0%, #2ea043 100%);
        color: white; font-size: 1.2rem; font-weight: 800; height: 4rem; border-radius: 12px; border: none;
    }
    .reset-btn button {
        background-color: #30363d !important; color: #f85149 !important; border: 1px solid #f85149 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 2. LOGICA DI RESET ATOMICO
# ==============================================================================
def atomic_reset():
    """Cancella ogni traccia di dati dalla sessione e resetta i widget."""
    for key in st.session_state.keys():
        del st.session_state[key]
    st.rerun()

# ==============================================================================
# 3. SIDEBAR: INPUT E CONTROLLI
# ==============================================================================
STILI_INVISIBILI = {
    "Saggio Scientifico": "high-end academic non-fiction, professional layout",
    "Quiz Scientifico": "educational quiz book, vibrant and dynamic background",
    "Manuale Tecnico": "industrial technical guide, blueprint schematic aesthetic",
    "Business": "luxury corporate style, gold and navy accents",
    "Romanzo Rosa": "ethereal romance, soft lighting, pastel emotional tones",
    "Thriller": "gritty suspense thriller, noir high-contrast shadows",
    "Fantasy": "epic fantasy world, magical atmospheric lighting",
    "Fantascienza": "cyberpunk sci-fi, futuristic tech HUD elements",
    "Manuale Psicologico": "serene psychology self-help, zen minimalist balance",
    "Biografia": "classic biography, elegant portraiture, vintage textures"
}

with st.sidebar:
    st.title("📕 DESIGNER v82")
    
    if st.button("🔄 NUOVO PROGETTO / RESET", key="reset_button", help="Cancella tutto e ricomincia"):
        atomic_reset()
    
    st.divider()
    genere_it = st.selectbox("Atmosfera Editoriale:", list(STILI_INVISIBILI.keys()), key="genere")
    
    st.divider()
    
    # Checkbox per attivazione testo
    use_t = st.checkbox("FORZA STAMPA TITOLO", value=True, key="use_t")
    t_val = st.text_input("Titolo:", value="PATENTE SUBITO", key="t_val") if use_t else ""
    t_pos = st.selectbox("Posizione Titolo:", ["top", "center", "bottom"], key="t_pos") if use_t else ""

    use_a = st.checkbox("FORZA STAMPA AUTORE", value=True, key="use_a")
    a_val = st.text_input("Autore:", value="ANTONINO STRAMERA", key="a_val") if use_a else ""
    a_pos = st.selectbox("Posizione Autore:", ["top", "center", "bottom"], index=2, key="a_pos") if use_a else ""

    st.divider()
    desc_it = st.text_area("Scena Visiva (IT):", key="desc_it")
    
    if st.button("🪄 1. GENERA ARCHITETTURA PROMPT"):
        if desc_it:
            with st.spinner("Prioritizzazione testo..."):
                scene_en = GoogleTranslator(source='it', target='en').translate(desc_it)
                stile_en = STILI_INVISIBILI.get(genere_it)
                
                # COSTRUZIONE MANDATORIA DEL TESTO (Anti-sparizione)
                text_layer = []
                # Nota: raddoppiamo i controlli per essere sicuri che Flux legga bene
                if use_t and t_val:
                    text_layer.append(f"MANDATORY: Print the title \"\"\"{t_val}\"\"\" in big, bold, 3D letters at the {t_pos} section.")
                if use_a and a_val:
                    text_layer.append(f"MANDATORY: Print the author name \"\"\"{a_val}\"\"\" in clear, sharp letters at the {a_pos} section.")
                
                # Prompt con Gerarchia Inviolabile
                prompt = (
                    f"TYPOGRAPHY OVERLAY (HIGHEST PRIORITY): {' '.join(text_layer)} "
                    f"BACKGROUND: A professional ebook cover, mood: {stile_en}, scene: {scene_en}. "
                    f"VISUAL RULES: Background must be simple and darker behind the text areas to ensure absolute legibility. "
                    f"CRITICAL: Do NOT write the word '{genere_it}'. Correct spelling for \"\"\"{t_val}\"\"\" and \"\"\"{a_val}\"\"\" is required. "
                    f"8k, cinematic lighting, sharp font rendering."
                )
                
                st.session_state['active_prompt'] = prompt
                st.success("Architettura pronta!")

# ==============================================================================
# 4. WORKSTATION DI PRODUZIONE
# ==============================================================================
st.title("🎨 Workstation v82 - Atomic Control")
col_l, col_r = st.columns([1.2, 1])

# Recupero prompt dalla sessione
current_prompt = st.session_state.get('active_prompt', "")
current_image = st.session_state.get('active_image', None)

with col_l:
    p_edit = st.text_area("Prompt Tecnico Attivo:", value=current_prompt, height=250)
    
    if st.button("🔥 2. GENERA COPERTINA HD"):
        if not p_edit:
            st.error("Configura il progetto nella sidebar!")
        else:
            client = replicate.Client(api_token=st.secrets["REPLICATE_API_TOKEN"])
            try:
                with st.spinner("Rendering in corso..."):
                    out = client.run(
                        "black-forest-labs/flux-1.1-pro",
                        input={"prompt": p_edit, "aspect_ratio": "2:3", "output_format": "jpg"}
                    )
                    st.session_state['active_image'] = str(out)
                    st.balloons()
            except Exception as e:
                st.error(f"Errore: {e}")

with col_r:
    st.subheader("🖼️ Anteprima Finale")
    if current_image:
        st.image(current_image, use_container_width=True)
        st.divider()
        st.download_button("📥 Scarica JPG", requests.get(current_image).content, "cover.jpg")
    else:
        st.info("In attesa di produzione...")
