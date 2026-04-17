"""
================================================================================
AI EBOOK PUBLISHER - THE CITADEL v76.0
================================================================================
ENGINE: Flux 1.1 Pro (Replicate)
DESIGN SYSTEM: Industrial Dark / GitHub Style
CAPABILITIES: Full Typography Control, Editorial Autonomy, Translation Matrix.
================================================================================
"""

import streamlit as st
import replicate
import requests
import time
import os
import datetime
import uuid
import json
from deep_translator import GoogleTranslator

# ------------------------------------------------------------------------------
# [MODULO 1: CONFIGURAZIONE CORE E SESSIONE]
# ------------------------------------------------------------------------------
APP_IDENTITY = "Citadel Editorial Engine"
BUILD_ID = "2026.04.17.V76"

if 'v76_prompt' not in st.session_state: st.session_state['v76_prompt'] = ""
if 'v76_res' not in st.session_state: st.session_state['v76_res'] = None
if 'sys_logs' not in st.session_state: st.session_state['sys_logs'] = []

def add_log(msg):
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    st.session_state['sys_logs'].append(f"[{ts}] {msg}")

# ------------------------------------------------------------------------------
# [MODULO 2: DESIGN SYSTEM - CSS ESTESO]
# ------------------------------------------------------------------------------
def apply_citadel_design():
    st.set_page_config(page_title="Citadel v76", page_icon="📕", layout="wide")
    
    st.markdown(f"""
    <style>
    /* Reset & Base */
    .stApp {{ background-color: #0d1117; color: #c9d1d9; font-family: 'Segoe UI', sans-serif; }}
    [data-testid="stSidebar"] {{ background-color: #161b22; border-right: 1px solid #30363d; min-width: 450px !important; }}
    #MainMenu, footer, header {{ visibility: hidden; }}

    /* Custom Scrollbar */
    ::-webkit-scrollbar {{ width: 8px; }}
    ::-webkit-scrollbar-track {{ background: #0d1117; }}
    ::-webkit-scrollbar-thumb {{ background: #30363d; border-radius: 10px; }}

    /* Input & Widgets */
    .stTextInput input, .stTextArea textarea, .stSelectbox div {{
        background-color: #0d1117 !important;
        color: #58a6ff !important;
        border: 1px solid #30363d !important;
        border-radius: 6px !important;
    }}
    
    /* Citadel Buttons */
    div.stButton > button:first-child {{
        background: linear-gradient(180deg, #238636 0%, #2ea043 100%);
        color: white; border-radius: 6px; border: 1px solid rgba(240,246,252,0.1);
        font-weight: 700; height: 3.8rem; width: 100%; transition: 0.2s;
    }
    div.stButton > button:hover {{ transform: translateY(-1px); box-shadow: 0 4px 12px rgba(0,0,0,0.5); }}

    /* Ebook Mockup */
    .book-frame {{
        perspective: 1000px;
        margin-top: 20px;
    }}
    .book-canvas {{
        width: 100%;
        max-width: 400px;
        aspect-ratio: 2/3;
        background-color: #161b22;
        border-radius: 4px 15px 15px 4px;
        box-shadow: 20px 20px 60px rgba(0,0,0,0.8);
        border-left: 12px solid #000;
        margin: auto;
        overflow: hidden;
        transition: transform 0.5s;
    }}
    .book-canvas:hover {{ transform: rotateY(-10deg); }}
    
    /* Terminal Console */
    .terminal-box {{
        background-color: #010409;
        border: 1px solid #30363d;
        border-radius: 6px;
        padding: 15px;
        font-family: 'Consolas', monospace;
        color: #7ee787;
        font-size: 0.85rem;
        height: 200px;
        overflow-y: auto;
    }}
    </style>
    """, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# [MODULO 3: MATRICE DI TRADUZIONE ED ESPANSIONE STILI]
# ------------------------------------------------------------------------------
# Qui inseriamo una logica vastissima per generare migliaia di combinazioni
STREAMS = {
    "Saggio Scientifico": {
        "en": "Modern Academic Non-Fiction",
        "tags": "clean, white space, technical charts, minimal sans-serif, professional.",
        "extra": "Add a small 'International Science Academy' emblem and a digital DNA helix texture."
    },
    "Quiz Scientifico": {
        "en": "Educational Interactive Quiz",
        "tags": "vibrant colors, 3d puzzle elements, pop-art style, highly engaging.",
        "extra": "Add a badge saying 'BRAIN TRAINING' and floating geometric particles."
    },
    "Manuale Tecnico": {
        "en": "Industrial Engineering Manual",
        "tags": "schematic, blueprint blue, technical font, heavy duty aesthetic.",
        "extra": "Add a 'Step-by-Step' corner fold effect and metallic texture overlays."
    },
    "Business": {
        "en": "Corporate Leadership Book",
        "tags": "luxury gold accents, serif bold fonts, architectural composition.",
        "extra": "Add a 'Wall Street Top Seller' stamp and abstract financial growth lines."
    },
    "Romanzo Rosa": {
        "en": "Contemporary Romance Novel",
        "tags": "dreamy lighting, soft bokeh, pastel gradients, emotional.",
        "extra": "Add a delicate handwriting script for the subtitle and heart-shaped dust particles."
    },
    "Thriller": {
        "en": "Crime Thriller / Mystery",
        "tags": "noir, cinematic shadows, gritty, mysterious, high contrast.",
        "extra": "Add a scary 'Based on a true story' blurb and blood-ink splatters."
    },
    "Fantasy": {
        "en": "Epic High Fantasy",
        "tags": "ethereal glow, mystical, ornate, painterly style.",
        "extra": "Add ancient rune engravings on the edges and a magical portal light effect."
    },
    "Fantascienza": {
        "en": "Cyberpunk Science Fiction",
        "tags": "neon, holographic, futuristic tech, cold space tones.",
        "extra": "Add binary code rain in the background and a cyborg eye reflection."
    },
    "Manuale Psicologico": {
        "en": "Self-Help / Psychology",
        "tags": "zen, calm, watercolor textures, minimalist, organic shapes.",
        "extra": "Add a mindfulness logo and soft lens flare at the top."
    },
    "Biografia": {
        "en": "Memoir / Biography",
        "tags": "vintage sepia, classic elegance, textured paper, timeless.",
        "extra": "Add a signature facsimile at the bottom and a grainy film effect."
    }
}

# ------------------------------------------------------------------------------
# [MODULO 4: PROMPT GENERATOR ENGINE]
# ------------------------------------------------------------------------------
def generate_complex_prompt(genre_it, scene_it, t_val, t_pos, a_val, a_pos):
    """Costruisce un prompt enterprise con controllo gerarchico del testo."""
    
    # 1. Recupero Dati Stile
    stream = STREAMS.get(genre_it, STREAMS["Business"])
    
    # 2. Traduzione Scena
    try:
        scene_en = GoogleTranslator(source='it', target='en').translate(scene_it)
    except:
        scene_en = scene_it
    
    # 3. Assemblaggio Regole Testo (FIX PRIORITÀ)
    text_commands = []
    if t_val:
        text_commands.append(f"STRICTLY PRINT the title \"{t_val}\" at the {t_pos} in huge letters.")
    if a_val:
        text_commands.append(f"STRICTLY PRINT the author name \"{a_val}\" at the {a_pos} in elegant letters.")
    
    # 4. Prompt Finale
    full_prompt = (
        f"Professional Book Cover for a {stream['en']}. "
        f"Visual content: {scene_en}. "
        f"Style: {stream['tags']} {stream['extra']} "
        f"Typography Layout: {' '.join(text_commands)} "
        f"CRITICAL: Do not write '{genre_it}' or any other text. Only the title and author. "
        f"8k resolution, cinematic lighting, editorial masterpiece, masterpiece composition."
    )
    return full_prompt

# ------------------------------------------------------------------------------
# [MODULO 5: MAIN INTERFACE]
# ------------------------------------------------------------------------------
def citadel_main():
    apply_citadel_design()
    
    # --- SIDEBAR ---
    with st.sidebar:
        st.title("🛡️ CITADEL v76")
        st.caption(f"Kernel Build: {BUILD_ID}")
        
        st.divider()
        g_choice = st.selectbox("Categoria:", list(STREAMS.keys()))
        
        # Gestione Titolo
        show_t = st.checkbox("Abilita Titolo", value=True)
        t_text = st.text_input("Titolo:", "Oltre l'Orizzonte") if show_t else ""
        t_pos = st.selectbox("Posizione Titolo:", ["top", "center", "bottom"]) if show_t else ""

        # Gestione Autore
        show_a = st.checkbox("Abilita Autore", value=True)
        a_text = st.text_input("Autore:", "Leonardo Da Vinci") if show_a else ""
        a_pos = st.selectbox("Posizione Autore:", ["top", "center", "bottom"], index=2) if show_a else ""

        st.divider()
        scene_it = st.text_area("Descrizione Scena (IT):", height=100)
        
        if st.button("🪄 1. GENERA ARCHITETTURA"):
            if scene_it:
                add_log(f"Inizio compilazione per genere: {g_choice}")
                p = generate_complex_prompt(g_choice, scene_it, t_text, t_pos, a_text, a_pos)
                st.session_state['v76_prompt'] = p
                add_log("Architettura prompt compilata con successo.")
                st.success("Prompt pronto!")
            else:
                st.warning("Descrizione mancante!")

    # --- MAIN AREA ---
    col_left, col_right = st.columns([1.3, 1])

    with col_left:
        st.header("⚙️ Editorial Terminal")
        p_edit = st.text_area("Final Prompt (EN):", value=st.session_state['v76_prompt'], height=280)
        
        if st.button("🚀 2. AVVIA RENDERING NEURALE"):
            if not p_edit:
                st.error("Generare prima l'architettura!")
            else:
                try:
                    client = replicate.Client(api_token=st.secrets["REPLICATE_API_TOKEN"])
                    add_log("Handshake con Replicate API...")
                    with st.spinner("Rendering in corso (Flux 1.1 Pro)..."):
                        output = client.run(
                            "black-forest-labs/flux-1.1-pro",
                            input={"prompt": p_edit, "aspect_ratio": "2:3", "output_format": "jpg"}
                        )
                        st.session_state['v76_res'] = str(output)
                        add_log("Immagine ricevuta correttamente.")
                        st.balloons()
                except Exception as e:
                    add_log(f"ERRORE: {str(e)}")
                    st.error(f"Errore: {e}")

        st.subheader("📡 System Logs")
        log_html = "<br>".join(st.session_state['sys_logs'][::-1])
        st.markdown(f'<div class="terminal-box">{log_html}</div>', unsafe_allow_html=True)

    with col_right:
        st.subheader("🖼️ Preview")
        if st.session_state['v76_res']:
            # FIX: Visualizzazione sicura con CSS
            res_url = st.session_state['v76_res']
            st.markdown(f"""
                <div class="book-frame">
                    <div class="book-canvas" style="background-image: url('{res_url}'); background-size: cover;"></div>
                </div>
            """, unsafe_allow_html=True)
            
            st.divider()
            st.download_button("💾 Download Cover HD", requests.get(res_url).content, "cover_citadel.jpg")
        else:
            st.markdown('<div class="book-canvas" style="display:flex;align-items:center;justify-content:center;color:#444;">Anteprima assente</div>', unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# AVVIO
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    citadel_main()
