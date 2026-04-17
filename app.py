import streamlit as st
import replicate
import requests
import os
from deep_translator import GoogleTranslator

# ==============================================================================
# 1. CONFIGURAZIONE E DESIGN
# ==============================================================================
st.set_page_config(page_title="Ebook Designer v83.1", page_icon="📕", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; min-width: 420px !important; }
    header, footer, .stAppDeployButton { display: none !important; }
    
    .stTextInput input, .stTextArea textarea, .stSelectbox div {
        background-color: #0d1117 !important; color: #58a6ff !important; border: 1px solid #30363d !important;
    }
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
        color: white; font-size: 1.1rem; font-weight: 800; height: 3.5rem; border-radius: 10px; border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 2. LOGICA RESET E SESSIONE
# ==============================================================================
if 'v83_prompt' not in st.session_state: st.session_state['v83_prompt'] = ""
if 'v83_res' not in st.session_state: st.session_state['v83_res'] = None

def reset_all():
    for key in st.session_state.keys():
        del st.session_state[key]
    st.rerun()

# ==============================================================================
# 3. MATRICE DEGLI STILI (DINAMICA CON NUOVE CATEGORIE)
# ==============================================================================
MODALITA_RENDERING = {
    "Fotorealistico": "photorealistic, 8k, highly detailed, realistic textures",
    "Illustrazione": "artistic illustration, hand-drawn style, vibrant colors, clean lines",
    "3D Render": "octane render, unreal engine 5, volumetric lighting, 3d depth",
    "Minimalista": "flat design, vector art, minimalist aesthetic, simple shapes",
    "Vintage": "retro oil painting style, aged paper texture, classic look"
}

ATMOSFERE = {
    "Saggio Scientifico": "clean academic layout, professional white space",
    "Quiz Scientifico": "dynamic educational layout, colorful background",
    "Manuale Tecnico": "technical schematic, industrial blueprint style",
    "Business": "corporate luxury, sharp contrast, gold accents",
    "Romanzo Rosa": "dreamy lighting, bokeh, soft pastel tones",
    "Thriller": "noir, dramatic shadows, high contrast dark tones",
    "Fantasy": "magical glow, epic landscape, mystical atmosphere",
    "Fantascienza": "cyberpunk, futuristic neon, space tech",
    "Manuale Psicologico": "zen, calm watercolor, minimalist balance",
    "Biografia": "vintage portrait, elegant typography, historical feel",
    "Religioso/Teologico": "sacred atmosphere, divine light rays, solemn and majestic composition, classical theological aesthetic",
    "Spirituale/Esoterico": "mystical vibes, occult symbols, ethereal fog, deep purple and gold tones, enigmatic atmosphere",
    "Meditazione": "peaceful serenity, soft focus, natural elements, zen harmony, light and airy composition"
}

# ==============================================================================
# 4. SIDEBAR: PERSONALIZZAZIONE TOTALE
# ==============================================================================
with st.sidebar:
    st.title("📕 DESIGNER v83.1")
    if st.button("🔄 RESET COMPLETO"): reset_all()
    
    st.divider()
    
    # 1. Scelta Atmosfera
    genere = st.selectbox("1. Atmosfera Editoriale:", list(ATMOSFERE.keys()))
    
    # 2. Scelta Tipo di Rendering
    tipo_render = st.selectbox("2. Stile di Rendering:", list(MODALITA_RENDERING.keys()))
    
    st.divider()
    
    # Testi (Mandatori)
    use_t = st.checkbox("Titolo", value=True)
    t_val = st.text_input("Testo Titolo:", "TITOLO ESEMPIO") if use_t else ""
    t_pos = st.selectbox("Posizione Titolo:", ["top", "center", "bottom"]) if use_t else ""

    use_a = st.checkbox("Autore", value=True)
    a_val = st.text_input("Nome Autore:", "AUTORE ESEMPIO") if use_a else ""
    a_pos = st.selectbox("Posizione Autore:", ["top", "center", "bottom"], index=2) if use_a else ""

    st.divider()
    desc_it = st.text_area("3. Scena Visiva (IT):", placeholder="Es: Un monaco in cima a una montagna...")
    
    if st.button("🪄 GENERA ARCHITETTURA"):
        if desc_it:
            with st.spinner("Compilazione..."):
                try:
                    t = GoogleTranslator(source='it', target='en')
                    scene_en = t.translate(desc_it)
                    
                    # CORREZIONE TIPOGRAFICA: Forzatura carattere per carattere
                    text_block = []
                    if use_t and t_val:
                        text_block.append(f"The cover must display the exact text \"{t_val}\" clearly as the main title at the {t_pos}.")
                    if use_a and a_val:
                        text_block.append(f"The cover must display the exact author name \"{a_val}\" clearly at the {a_pos}.")
                    
                    # Composizione Prompt finale con istruzioni di controllo ortografico (Spell-check enforcement)
                    prompt = (
                        f"TYPOGRAPHY OVERLAY: {' '.join(text_block)} "
                        f"BACKGROUND: A professional ebook cover with {scene_en}. "
                        f"ART STYLE: {ATMOSFERE[genere]} combined with {MODALITA_RENDERING[tipo_render]}. "
                        f"MANDATORY RULES: 1. Render the text exactly as written in quotes. 2. No extra characters or invented letters. 3. High contrast between text and background. 4. Do not write the word '{genere}' on the image."
                    )
                    st.session_state['v83_prompt'] = prompt
                    st.success("Prompt creato con correzione tipografica!")
                except Exception as e:
                    st.error(f"Errore traduzione: {e}")

# ==============================================================================
# 5. WORKSTATION
# ==============================================================================
st.title("🎨 Custom Creative Workstation")
col_l, col_r = st.columns([1.2, 1])

with col_l:
    p_edit = st.text_area("Prompt Finale (EN):", value=st.session_state['v83_prompt'], height=250)
    
    if st.button("🔥 GENERA COPERTINA"):
        if not p_edit:
            st.error("Crea prima l'architettura nella sidebar!")
        else:
            if "REPLICATE_API_TOKEN" not in st.secrets:
                st.error("API Token non configurato nei Secrets!")
            else:
                client = replicate.Client(api_token=st.secrets["REPLICATE_API_TOKEN"])
                try:
                    with st.spinner("L'IA sta elaborando la tua copertina..."):
                        out = client.run(
                            "black-forest-labs/flux-1.1-pro",
                            input={
                                "prompt": p_edit, 
                                "aspect_ratio": "2:3", 
                                "output_format": "jpg",
                                "output_quality": 100
                            }
                        )
                        st.session_state['v83_res'] = str(out)
                        st.balloons()
                except Exception as e:
                    st.error(f"Errore generazione: {e}")

with col_r:
    st.subheader("🖼️ Anteprima")
    if st.session_state['v83_res']:
        st.image(st.session_state['v83_res'], use_container_width=True)
        st.divider()
        try:
            response = requests.get(st.session_state['v83_res'])
            st.download_button("📥 Scarica Copertina HD", response.content, "cover.jpg", "image/jpeg")
        except:
            st.warning("Errore nel caricamento del file per il download.")
    else:
        st.info("Configura il progetto e clicca su Genera.")
