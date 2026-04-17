import streamlit as st
import replicate
import requests
import os
import random
from deep_translator import GoogleTranslator

# ==============================================================================
# 1. CONFIGURAZIONE E STILE PREMUM
# ==============================================================================
st.set_page_config(page_title="Ebook Auto-Publisher v70", page_icon="📕", layout="wide")

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

    /* Pulsante Master */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #8250df 0%, #6639b7 100%);
        color: white; font-size: 1.2rem; font-weight: 800; height: 4rem;
        border-radius: 12px; width: 100%; border: none; box-shadow: 0 4px 15px rgba(102, 57, 183, 0.4);
    }
    
    /* Preview Libro 3D-Style */
    .ebook-preview {
        border-radius: 4px 15px 15px 4px;
        box-shadow: 25px 25px 60px rgba(0,0,0,0.9);
        border-left: 12px solid #111; /* Costa del libro */
        max-width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 2. LOGICA DI PROMPT ENGINEERING AVANZATA (TESTO AUTONOMO)
# ==============================================================================
def generate_editorial_prompt(genre, scene, title, author, t_pos, a_pos):
    """Costruisce un prompt che istruisce l'IA a creare testo autonomo."""
    
    t_coord = t_pos.replace('In ', '').replace('Al ', '').lower()
    a_coord = a_pos.replace('In ', '').replace('Al ', '').lower()
    
    # 1. Base del prompt
    prompt = (
        f"A professional, award-winning ebook cover design for a {genre} book. "
        f"Visual scene: {scene}. "
        f"Cinematic lighting, high contrast, photorealistic, 8k. "
    )
    
    # 2. Inserimento testi dell'utente
    if title:
        prompt += f"The main title '{title}' must be prominent, perfectly spelled, and placed at the {t_coord} with beautiful typography. "
    if author:
        prompt += f"The author name '{author}' must be clearly written at the {a_coord}. "
        
    # 3. Logica Autonoma: Aggiunta di scritte coerenti non richieste
    editorial_additions = {
        "Saggio Scientifico": "Add a realistic technical subtitle below the main title, a small 'Science Journal' logo, and some faded mathematical formulas in the background.",
        "Quiz Scientifico": "Add a badge that says 'OVER 500 QUESTIONS' and a 'Brain Power' series logo.",
        "Manuale Tecnico": "Add a 'Step-by-Step Guide' banner and a fake version number like 'Vol. 3 / Ed. 2026'.",
        "Business": "Add a subtitle like 'Strategies for success in the digital age' and a fictional 'Wall Street Bestseller' stamp.",
        "Romanzo Rosa": "Add a romantic quote in script font near the bottom and a 'Heartfelt Stories' collection logo.",
        "Thriller": "Add a gritty, scary subtitle like 'The truth will bleed' and an acclaimed critic's blurb at the top.",
        "Fantasy": "Add ancient rune textures, a magical series name, and an ornate, decorative border.",
        "Fantascienza": "Add tech-style HUD overlays, a space-corp logo, and some unreadable binary code patterns.",
        "Manuale Psicologico": "Add a supportive subtitle like 'Find your inner peace' and a 'Mindfulness Series' badge.",
        "Biografia": "Add dates like '1950 - 2025' and a subtitle like 'The authorized story of a legend'."
    }
    
    # Se il genere è nella lista, aggiunge le istruzioni specifiche, altrimenti usa un default generico
    prompt += editorial_additions.get(genre, "Add a generic bestselling book blurb at the top and a publisher logo at the bottom.")
    
    # 4. Vincoli di design
    prompt += " Crucial: All autonomous text must be aesthetically integrated, realistic, and coherent with the visual style, creating a believable full book cover."
    
    return prompt

# ==============================================================================
# 3. SIDEBAR CON LOGICA EDITORIALE
# ==============================================================================
with st.sidebar:
    st.title("📕 EDITORIAL v70")
    st.caption("AI Full Cover Autonomy")
    st.divider()
    
    lista_generi = [
        "Saggio Scientifico", "Quiz Scientifico", "Manuale Tecnico",
        "Business", "Romanzo Rosa", "Thriller", 
        "Fantasy", "Fantascienza", "Manuale Psicologico", "Biografia"
    ]
    genre = st.selectbox("Categoria Letteraria:", lista_generi)
    
    st.divider()
    
    # Testi Utente
    t_text = st.text_input("Titolo principale:", placeholder="es. Il Codice Quantico")
    t_pos = st.selectbox("Posizione Titolo:", ["In alto", "Al centro", "In basso"])

    a_text = st.text_input("Nome Autore:", placeholder="es. Dott.ssa Elena Vega")
    a_pos = st.selectbox("Posizione Autore:", ["In alto", "Al centro", "In basso"], index=2)

    st.divider()
    desc_it = st.text_area("Descrizione Visiva (IT):", placeholder="es. Un tunnel di luce particellare che esplode")
    
    if st.button("🪄 GENERA CONCEPT COMPLETO"):
        if desc_it:
            with st.spinner("L'IA sta elaborando il layout editoriale..."):
                t = GoogleTranslator(source='it', target='en')
                scene_en = t.translate(desc_it)
                
                # Chiama la logica avanzata
                p_base = generate_editorial_prompt(genre, scene_en, t_text, a_text, t_pos, a_pos)
                
                st.session_state['p_final'] = p_base
                st.success("Layout editoriale pronto!")

# ==============================================================================
# 4. AREA PRODUZIONE E PREVIEW
# ==============================================================================
st.title("🎨 Produzione Copertine Professionali")
st.caption("Configurazione: Flux 1.1 Pro (Gestione Testo Avanzata)")

col_l, col_r = st.columns([1.2, 1])

if 'p_final' not in st.session_state: st.session_state['p_final'] = ""
if 'res_url' not in st.session_state: st.session_state['res_url'] = None

with col_l:
    p_area = st.text_area("Prompt Tecnico Autonomo:", value=st.session_state['p_final'], height=250)
    
    if st.button("🔥 CREA COPERTINA FULL-AUTO"):
        if not p_area:
            st.error("Configura il concept
