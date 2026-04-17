import streamlit as st
import replicate
import requests
import os
from deep_translator import GoogleTranslator

# ==============================================================================
# 1. DESIGN E CONFIGURAZIONE UI
# ==============================================================================
st.set_page_config(page_title="Ebook Designer v81", page_icon="📕", layout="wide")

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
# 2. LOGICA DI STILE INVISIBILE
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

# ==============================================================================
# 3. SIDEBAR: LOGICA DI FORZATURA TESTO
# ==============================================================================
with st.sidebar:
    st.title("📕 DESIGNER v81")
    st.caption("Typography Enforcement Mode")
    
    if st.button("🔄 NUOVO PROGETTO / RESET"):
        st.session_state.clear()
        st.rerun()
    
    st.divider()
    genere_it = st.selectbox("Atmosfera Editoriale:", list(STILI_INVISIBILI.keys()))
    
    st.divider()
    
    # Checkbox e Input
    use_t = st.checkbox("FORZA STAMPA TITOLO", value=True)
    t_val = st.text_input("Titolo:", "PATENTE SUBITO") if use_t else ""
    t_pos = st.selectbox("Posizione Titolo:", ["top", "center", "bottom"]) if use_t else ""

    use_a = st.checkbox("FORZA STAMPA AUTORE", value=True)
    a_val = st.text_input("Autore:", "ANTONINO STRAMERA") if use_a else ""
    a_pos = st.selectbox("Posizione Autore:", ["top", "center", "bottom"], index=2) if use_a else ""

    st.divider()
    desc_it = st.text_area("Scena Visiva (IT):")
    
    if st.button("🪄 GENERA ARCHITETTURA"):
        if desc_it:
            with st.spinner("Prioritizzazione testo in corso..."):
                t = GoogleTranslator(source='it', target='en')
                scene_en = t.translate(desc_it)
                stile_en = STILI_INVISIBILI.get(genere_it)
                
                # TECNICA DI ENFORCEMENT (LOGICA LAYERED)
                # Mettiamo il testo come PRIMO elemento del prompt per massima priorità
                text_layer = []
                if use_t and t_val:
                    text_layer.append(f"MANDATORY: The title \"\"\"{t_val}\"\"\" must be perfectly printed in a massive, bold, highly visible font at the {t_pos} section.")
                if use_a and a_val:
                    text_layer.append(f"MANDATORY: The author name \"\"\"{a_val}\"\"\" must be perfectly printed in a clear, sharp, visible font at the {a_pos} section.")
                
                # Costruzione del prompt con "Hard Constraints"
                prompt = (
                    f"TYPOGRAPHY OVERLAY (HIGHEST PRIORITY): {' '.join(text_layer)} "
                    f"BACKGROUND SCENE (SECONDARY): A professional ebook cover for a {stile_en} with {scene_en}. "
                    f"VISUAL HIERARCHY: The background must be simplified or slightly darkened behind the text areas to ensure the typography is the most prominent element. "
                    f"CRITICAL RULES: Do NOT write '{genere_it}'. No spelling errors in \"\"\"{t_val}\"\"\" and \"\"\"{a_val}\"\"\". All letters must be visible. "
                    f"8k, cinematic lighting, sharp font rendering, graphic design masterpiece."
                )
                
                st.session_state['v81_prompt'] = prompt
                st.success("Architettura con priorità testo pronta!")

# ==============================================================================
# 4. WORKSTATION DI PRODUZIONE
# ==============================================================================
st.title("🎨 Workstation v81 - Hard-Typography")
col_l, col_r = st.columns([1.2, 1])

if 'v81_prompt' not in st.session_state: st.session_state['v81_prompt'] = ""
if 'v81_res' not in st.session_state: st.session_state['v81_res'] = None

with col_l:
    p_edit = st.text_area("Prompt Tecnico (EN):", value=st.session_state['v81_prompt'], height=250)
    
    if st.button("🔥 GENERA COPERTINA HD"):
        if not p_edit:
            st.error("Configura il progetto nella sidebar!")
        else:
            client = replicate.Client(api_token=st.secrets["REPLICATE_API_TOKEN"])
            try:
                with st.spinner("Esecuzione Rendering (Typography Mode)..."):
                    out = client.run(
                        "black-forest-labs/flux-1.1-pro",
                        input={
                            "prompt": p_edit,
                            "aspect_ratio": "2:3",
                            "output_format": "jpg"
                        }
                    )
                    st.session_state['v81_res'] = str(out)
                    st.balloons()
            except Exception as e:
                st.error(f"Errore API: {e}")

with col_r:
    st.subheader("🖼️ Anteprima Finale")
    if st.session_state['v81_res']:
        st.image(st.session_state['v81_res'], use_container_width=True)
        st.divider()
        st.download_button("📥 Scarica JPG", requests.get(st.session_state['v81_res']).content, "cover.jpg")
    else:
        st.info("In attesa di produzione...")

st.caption("v81.0 - Mandatory Typography | Layered Prompting | Flux 1.1 Pro")
