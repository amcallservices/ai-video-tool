import streamlit as st
import replicate
import requests
import os
import datetime
from deep_translator import GoogleTranslator

# ==============================================================================
# 1. CONFIGURAZIONE E DESIGN SYSTEM (FIX SYNTAX ERROR)
# ==============================================================================
st.set_page_config(page_title="Ebook Designer v77", page_icon="📕", layout="wide")

# Usiamo le doppie parentesi {{ }} per evitare il SyntaxError nelle f-strings
st.markdown(f"""
    <style>
    .stApp {{ 
        background-color: #0d1117; 
        color: #c9d1d9; 
    }}
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
        background: linear-gradient(135deg, #238636 0%, #2ea043 100%);
        color: white; font-size: 1.2rem; font-weight: 800; height: 4rem;
        border-radius: 10px; width: 100%; border: none;
    }}
    
    .ebook-preview-container {{
        padding: 20px;
        display: flex;
        justify-content: center;
    }}

    .ebook-3d {{
        border-radius: 4px 15px 15px 4px;
        box-shadow: 25px 25px 60px rgba(0,0,0,0.9);
        border-left: 12px solid #111;
        max-width: 100%;
        aspect-ratio: 2/3;
    }}
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 2. MATRICE DI TRADUZIONE GENERI
# ==============================================================================
STILI_EDITORIALI = {
    "Saggio Scientifico": "Modern Academic Science Essay, clean layout, professional",
    "Quiz Scientifico": "Science Quiz Book, vibrant and educational style, dynamic",
    "Manuale Tecnico": "Technical Manual, industrial engineering, blueprint aesthetic",
    "Business": "Corporate Business, luxury gold and navy accents, authoritative",
    "Romanzo Rosa": "Romance Novel, soft lighting, pastel colors, emotional",
    "Thriller": "Crime Thriller, high contrast noir, dark and mysterious",
    "Fantasy": "High Fantasy, magical elements, ornate mystical atmosphere",
    "Fantascienza": "Sci-Fi, cyberpunk HUD, futuristic technology, space",
    "Manuale Psicologico": "Psychology Self-Help, serene zen colors, minimalist balance",
    "Biografia": "Historical Biography, classic elegant portrait, vintage paper"
}

# ==============================================================================
# 3. SIDEBAR: LOGICA LAYOUT CUSTOM
# ==============================================================================
with st.sidebar:
    st.title("📕 DESIGNER v77")
    st.caption("Fix: Syntax & Layout Priority")
    st.divider()
    
    genere_it = st.selectbox("Categoria:", list(STILI_EDITORIALI.keys()))
    
    st.divider()
    
    # Toggle Titolo
    show_t = st.checkbox("Inserisci Titolo", value=True)
    t_val = st.text_input("Testo Titolo:", "L'Ultima Scorreria") if show_t else ""
    t_pos = st.selectbox("Posizione Titolo:", ["top", "center", "bottom"]) if show_t else ""

    # Toggle Autore
    show_a = st.checkbox("Inserisci Autore", value=True)
    a_val = st.text_input("Testo Autore:", "Marco Valerio") if show_a else ""
    a_pos = st.selectbox("Posizione Autore:", ["top", "center", "bottom"], index=2) if show_a else ""

    st.divider()
    desc_it = st.text_area("Scena Visiva (IT):", placeholder="Es: Una astronave che orbita intorno a un pianeta rosso")
    
    if st.button("🪄 GENERA ARCHITETTURA PROMPT"):
        if desc_it:
            with st.spinner("Compilazione neurale..."):
                # Traduzione Scena
                scene_en = GoogleTranslator(source='it', target='en').translate(desc_it)
                stile_en = STILI_EDITORIALI.get(genere_it)
                
                # Costruzione Regole Testo
                regole_testo = []
                if show_t and t_val:
                    regole_testo.append(f"STRICTLY PRINT the title \"{t_val}\" at the {t_pos} of the image.")
                if show_a and a_val:
                    regole_testo.append(f"STRICTLY PRINT the author name \"{a_val}\" at the {a_pos} of the image.")
                
                # Prompt Master
                prompt_final = (
                    f"A professional ebook cover for a {stile_en}. "
                    f"Visual content: {scene_en}. "
                    f"{' '.join(regole_testo)} "
                    f"Editorial autonomy: Add extra text like small subtitles, logos and series names consistent with {genere_it}. "
                    f"CRITICAL: Do not write '{genere_it}' on the cover. Only title and author provided. "
                    f"8k, cinematic lighting, book cover composition."
                )
                
                st.session_state['v77_prompt'] = prompt_final
                st.success("Prompt pronto!")

# ==============================================================================
# 4. WORKSTATION DI PRODUZIONE
# ==============================================================================
st.title("🎨 AI Cover Workstation")
col_l, col_r = st.columns([1.3, 1])

if 'v77_prompt' not in st.session_state: st.session_state['v77_prompt'] = ""
if 'v77_res' not in st.session_state: st.session_state['v77_res'] = None

with col_l:
    p_edit = st.text_area("Prompt Tecnico (EN):", value=st.session_state['v77_prompt'], height=250)
    
    if st.button("🔥 AVVIA RENDERING"):
        if not p_edit:
            st.error("Usa la sidebar per generare il prompt!")
        else:
            try:
                client = replicate.Client(api_token=st.secrets["REPLICATE_API_TOKEN"])
                with st.spinner("Rendering Flux 1.1 Pro..."):
                    out = client.run(
                        "black-forest-labs/flux-1.1-pro",
                        input={"prompt": p_edit, "aspect_ratio": "2:3", "output_format": "jpg"}
                    )
                    st.session_state['v77_res'] = str(out)
                    st.balloons()
            except Exception as e:
                st.error(f"Errore: {e}")

with col_r:
    st.subheader("🖼️ Anteprima Editoriale")
    if st.session_state['v77_res']:
        # Mostriamo l'immagine senza parametri illegali
        st.image(st.session_state['v77_res'], use_container_width=True)
        st.divider()
        st.download_button("💾 Scarica Copertina HD", requests.get(st.session_state['v77_res']).content, "cover.jpg")
    else:
        st.info("In attesa di produzione...")

st.caption("v77.0 - Syntax Fixed | Dual-Brace CSS | Flux 1.1 Pro")
