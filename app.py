import streamlit as st
import replicate
import requests
import os
from deep_translator import GoogleTranslator

# ==============================================================================
# 1. DESIGN E CONFIGURAZIONE UI
# ==============================================================================
st.set_page_config(page_title="Ebook Designer Pro v79", page_icon="📕", layout="wide")

st.markdown("""
    <style>
    .stApp {{ background-color: #0d1117; color: #c9d1d9; }}
    [data-testid="stSidebar"] {{ 
        background-color: #161b22; 
        border-right: 1px solid #30363d; 
        min-width: 400px !important; 
    }}
    #MainMenu, footer, header {{ visibility: hidden; }}
    
    .stTextInput input, .stTextArea textarea, .stSelectbox div {{
        background-color: #0d1117 !important;
        color: #58a6ff !important;
        border: 1px solid #30363d !important;
    }}

    div.stButton > button:first-child {{
        background: linear-gradient(135deg, #fbbf24 0%, #d97706 100%);
        color: black; font-size: 1.2rem; font-weight: 800; height: 4rem;
        border-radius: 12px; width: 100%; border: none; box-shadow: 0 4px 15px rgba(217, 119, 6, 0.4);
    }}
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 2. DIZIONARIO STILI EDITORIALI
# ==============================================================================
STILI_EDITORIALI = {
    "Saggio Scientifico": "Academic Non-Fiction, professional white space, high legibility.",
    "Quiz Scientifico": "Educational Quiz, vibrant colors, clear bold labels.",
    "Manuale Tecnico": "Technical Guide, blueprint style, high-contrast schematic.",
    "Business": "Corporate Luxury, clean minimalist background, elegant gold/white text.",
    "Romanzo Rosa": "Romance Novel, dreamlike but with clear readable typography.",
    "Thriller": "Suspense Thriller, noir contrast, glowing text on dark background.",
    "Fantasy": "Epic Fantasy, ornate but sharp readable fonts, magical clarity.",
    "Fantascienza": "Sci-Fi, futuristic neon typography, sharp tech overlays.",
    "Manuale Psicologico": "Self-Help, clean zen background, airy and legible layout.",
    "Biography": "Biography, classic centered typography, high-end portrait lighting."
}

# ==============================================================================
# 3. SIDEBAR: CONTROLLI PER RISALTO TESTO
# ==============================================================================
with st.sidebar:
    st.title("📚 DESIGNER v79")
    st.caption("Focus: High Visibility Typography")
    st.divider()
    
    genere_it = st.selectbox("Categoria:", list(STILI_EDITORIALI.keys()))
    
    st.divider()
    
    # Titolo in evidenza
    use_t = st.checkbox("Metti in rilievo Titolo", value=True)
    t_val = st.text_input("Testo Titolo:", "PATENTE SUBITO") if use_t else ""
    t_pos = st.selectbox("Posizione Titolo:", ["top", "center", "bottom"]) if use_t else ""

    # Autore in evidenza
    use_a = st.checkbox("Metti in rilievo Autore", value=True)
    a_val = st.text_input("Testo Autore:", "ANTONINO STRAMERA") if use_a else ""
    a_pos = st.selectbox("Posizione Autore:", ["top", "center", "bottom"], index=2) if use_a else ""

    st.divider()
    desc_it = st.text_area("Descrizione Scena (IT):", placeholder="Descrivi lo sfondo della copertina...")
    
    if st.button("🪄 GENERA ARCHITETTURA"):
        if desc_it:
            with st.spinner("Ottimizzazione contrasto..."):
                t = GoogleTranslator(source='it', target='en')
                scene_en = t.translate(desc_it)
                stile_en = STILI_EDITORIALI.get(genere_it)
                
                # REGOLE DI RILIEVO (ULTRA CONTRAST LOGIC)
                text_rules = []
                if use_t and t_val:
                    text_rules.append(f"The title \"\"\"{t_val}\"\"\" must be the main focal point, using massive bold 3D typography at the {t_pos}. Use high contrast colors against the background.")
                if use_a and a_val:
                    text_rules.append(f"The author name \"\"\"{a_val}\"\"\" must be extremely sharp and visible at the {a_pos}, isolated on a clean part of the image to ensure perfect readability.")
                
                prompt = (
                    f"A high-end book cover design for a {stile_en}. "
                    f"Background: {scene_en}. "
                    f"TYPOGRAPHY OVERLAY: {' '.join(text_rules)} "
                    f"VISUAL HIERARCHY: Background elements must be slightly out of focus or simplified behind the text areas to make the typography pop. "
                    f"CRITICAL: Exact spelling for \"\"\"{t_val}\"\"\" and \"\"\"{a_val}\"\"\". No overlapping with background details. "
                    f"8k, cinematic lighting, sharp text rendering, professional publishing quality."
                )
                
                st.session_state['v79_prompt'] = prompt
                st.success("Prompt ad alta visibilità generato!")

# ==============================================================================
# 4. PRODUZIONE E ANTEPRIMA
# ==============================================================================
st.title("🎨 Workstation v79 - High Contrast")
col_l, col_r = st.columns([1.2, 1])

if 'v79_prompt' not in st.session_state: st.session_state['v79_prompt'] = ""
if 'v79_res' not in st.session_state: st.session_state['v79_res'] = None

with col_l:
    p_edit = st.text_area("Prompt Tecnico (EN):", value=st.session_state['v79_prompt'], height=250)
    
    if st.button("🔥 GENERA COPERTINA"):
        if not p_edit:
            st.error("Configura il prompt nella sidebar!")
        else:
            client = replicate.Client(api_token=st.secrets["REPLICATE_API_TOKEN"])
            try:
                with st.spinner("Rendering Flux 1.1 Pro (Ultra-Legibility Mode)..."):
                    out = client.run(
                        "black-forest-labs/flux-1.1-pro",
                        input={
                            "prompt": p_edit,
                            "aspect_ratio": "2:3",
                            "output_format": "jpg",
                            "output_quality": 100
                        }
                    )
                    st.session_state['v79_res'] = str(out)
                    st.balloons()
            except Exception as e:
                st.error(f"Errore API: {e}")

with col_r:
    st.subheader("🖼️ Risultato ad Alto Rilievo")
    if st.session_state['v79_res']:
        st.image(st.session_state['v79_res'], use_container_width=True)
        st.divider()
        st.download_button("📥 Scarica JPG", requests.get(st.session_state['v79_res']).content, "cover_high_res.jpg")
    else:
        st.info("In attesa di produzione...")
