import streamlit as st
import replicate
import requests
import os
import PyPDF2
from deep_translator import GoogleTranslator

# ==============================================================================
# 1. CONFIGURAZIONE E DESIGN (INVARIATO)
# ==============================================================================
st.set_page_config(page_title="Ebook Designer v89.0 - Genre Authority", page_icon="📕", layout="wide")

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
    .pdf-uploader-box { border: 2px dashed #007bff; padding: 15px; border-radius: 8px; margin-bottom: 15px; background-color: #10141b; }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 2. LOGICA RESET E SESSIONE (INVARIATO)
# ==============================================================================
if 'v83_prompt' not in st.session_state: st.session_state['v83_prompt'] = ""
if 'v83_res' not in st.session_state: st.session_state['v83_res'] = None
if 'auto_desc' not in st.session_state: st.session_state['auto_desc'] = ""

def reset_all():
    for key in st.session_state.keys():
        del st.session_state[key]
    st.rerun()

# ==============================================================================
# 3. KNOWLEDGE BASE NARRATIVA ADATTIVA
# ==============================================================================
class PDFSemanticPsychologyAnalyzer:
    @staticmethod
    def extract_text_from_pdf(pdf_file, max_pages=10):
        try:
            reader = PyPDF2.PdfReader(pdf_file)
            text_content = ""
            limit = min(max_pages, len(reader.pages))
            for i in range(limit):
                page = reader.pages[i]
                text_content += page.extract_text() + " "
            return text_content
        except Exception as e:
            st.error(f"Errore nella lettura del PDF: {e}")
            return None

    @staticmethod
    def generate_psychological_concept(text, api_token, genere_scelto):
        try:
            client = replicate.Client(api_token=api_token)
            # L'LLM ora riceve il genere come contesto per adattare la scena
            system_prompt = f"""
            Sei un Art Director editoriale senior esperto in {genere_scelto}. 
            Analizza l'estratto del libro e progetta una scena visiva per la copertina che sia TASSATIVAMENTE coerente con il genere '{genere_scelto}'.
            
            REGOLE PER GENERE:
            - Se è Scientifico/Tecnico: focus su ordine, precisione, icone pulite.
            - Se è Narrativo (Fantasy/Thriller): focus su atmosfera, tensione, personaggi.
            - Se è Ricettario: focus su cibo, freschezza, texture appetitose.
            - Se è Esoterico/Meditativo: focus su simbolismo, luce soffusa, colori spirituali.
            
            ESTRATTO: {text[:6000]}
            
            OUTPUT: Scrivi SOLO la scena visiva in 3 frasi in italiano.
            """
            output = client.run(
                "meta/meta-llama-3-8b-instruct",
                input={"prompt": system_prompt, "max_tokens": 250, "temperature": 0.6}
            )
            return "".join(output)
        except Exception as e:
            st.error(f"Errore Motore LLM: {e}")
            return None

# ==============================================================================
# 4. MATRICE DEGLI STILI (DINAMICA AGGIORNATA)
# ==============================================================================
MODALITA_RENDERING = {
    "Fotorealistico": "photorealistic, 8k, highly detailed",
    "Illustrazione": "artistic digital illustration, vibrant",
    "3D Render": "octane render, unreal engine 5, 3d depth",
    "Minimalista": "flat design, vector art, minimalist",
    "Vintage": "retro oil painting style, aged paper"
}

# NUOVE ATMOSFERE RICHIESTE CON DESCRITTORI TECNICI ADATTATI
ATMOSFERE = {
    "Saggio Scientifico": "authoritative academic layout, clean white space, mathematical or data precision",
    "Quiz Scientifico": "engaging educational layout, dynamic colorful diagrams, vibrant and fun",
    "Manuale Tecnico": "precise industrial schematic style, blueprint aesthetic, clean technical lines",
    "Religioso/Teologico": "sacred atmosphere, divine light rays, solemn and majestic classical composition",
    "Spirituale/Esoterico": "mystical vibes, occult symbols, ethereal fog, deep purple and gold palette",
    "Meditazione / Mindfulness": "peaceful serenity, zen harmony, soft focus, airy natural elements",
    "Business & Marketing": "modern corporate luxury, gold accents, sharp professional contrast, high-end branding",
    "Romanzo Rosa": "dreamy lighting, bokeh effect, soft pastel tones, emotional and romantic",
    "Thriller / Noir": "suspenseful noir, cinematic shadows, high contrast, dark and gritty mood",
    "Fantasy": "epic magical atmosphere, mystical glowing elements, ornate legendary landscape",
    "Fantascienza": "cyberpunk tech aesthetic, futuristic neon, space-age textures, sci-fi HUD",
    "Manuale Psicologico": "balanced zen minimalist layout, calming watercolor textures, psychological harmony",
    "Biografia": "classic biography portrait, elegant typography, timeless historical textures",
    "Ricettario": "gourmet food photography style, bright appetizing colors, fresh ingredients in focus",
    "Test Prep (Preparazione Esami)": "organized textbook style, academic focus icons, professional structured layout"
}

# ==============================================================================
# 5. SIDEBAR: PERSONALIZZAZIONE E ANALISI
# ==============================================================================
with st.sidebar:
    st.title("📕 DESIGNER v89.0")
    if st.button("🔄 RESET COMPLETO"): reset_all()
    
    st.divider()
    # Caricamento dinamico delle nuove atmosfere
    genere = st.selectbox("1. Atmosfera Editoriale:", list(ATMOSFERE.keys()))
    tipo_render = st.selectbox("2. Stile di Rendering:", list(MODALITA_RENDERING.keys()))
    
    st.divider()
    
    use_t = st.checkbox("Abilita Inserimento Titolo", value=True)
    t_val = st.text_input("Testo Titolo:", "TITOLO ESEMPIO") if use_t else ""
    t_pos = st.selectbox("Posizione Titolo:", ["top", "center", "bottom"]) if use_t else ""

    use_a = st.checkbox("Abilita Inserimento Autore", value=True)
    a_val = st.text_input("Nome Autore:", "AUTORE ESEMPIO") if use_a else ""
    a_pos = st.selectbox("Posizione Autore:", ["top", "center", "bottom"], index=2) if use_a else ""

    st.divider()

    # Modulo PDF
    st.markdown('<div class="pdf-uploader-box">', unsafe_allow_html=True)
    st.markdown(f"📄 **Analisi per {genere}**")
    uploaded_pdf = st.file_uploader("Carica il PDF del libro:", type=["pdf"])
    
    if uploaded_pdf is not None:
        if st.button("🧠 Avvia Profilazione Narrativa"):
            if "REPLICATE_API_TOKEN" not in st.secrets:
                st.error("Token mancante!")
            else:
                with st.spinner(f"Analisi specifica per genere {genere}..."):
                    txt = PDFSemanticPsychologyAnalyzer.extract_text_from_pdf(uploaded_pdf)
                    if txt:
                        # Passiamo il genere al generatore di concetti
                        ai_scene = PDFSemanticPsychologyAnalyzer.generate_psychological_concept(txt, st.secrets["REPLICATE_API_TOKEN"], genere)
                        if ai_scene:
                            st.session_state['auto_desc'] = ai_scene
                            st.success(f"Scena per '{genere}' generata!")
    st.markdown('</div>', unsafe_allow_html=True)

    desc_it = st.text_area("3. Scena Visiva (IT):", value=st.session_state['auto_desc'])
    
    # --- INTEGRAZIONE TASSATIVA TESTO ---
    if st.button("🪄 GENERA ARCHITETTURA"):
        if desc_it:
            with st.spinner("Compilazione prompt..."):
                try:
                    t = GoogleTranslator(source='it', target='en')
                    scene_en = t.translate(desc_it)
                    
                    text_enforcement = ""
                    if use_t and t_val:
                        text_enforcement += f"MANDATORY: The book title \"{t_val.upper()}\" must be printed in massive bold letters at the {t_pos}. "
                    if use_a and a_val:
                        text_enforcement += f"MANDATORY: The author name \"{a_val.upper()}\" must be clearly printed at the {a_pos}. "

                    prompt = (
                        f"TYPOGRAPHY HIGHEST PRIORITY. {text_enforcement} "
                        f"COVER SCENE: A professional ebook cover for a {genere} book, representing: {scene_en}. "
                        f"VISUAL STYLE: {ATMOSFERE[genere]} with {MODALITA_RENDERING[tipo_render]} rendering. "
                        f"CRITICAL RULES: 1. Render exactly the characters in quotes. 2. DO NOT OMIT the title or author. "
                        f"3. High contrast: background must be simplified behind the text to ensure 100% legibility."
                    )
                    st.session_state['v83_prompt'] = prompt
                    st.success(f"Architettura per {genere} pronta.")
                except Exception as e:
                    st.error(f"Errore: {e}")

# ==============================================================================
# 6. WORKSTATION GENERAZIONE (INVARIATO)
# ==============================================================================
st.title("🎨 Custom Creative Workstation")
col_l, col_r = st.columns([1.2, 1])

with col_l:
    p_edit = st.text_area("Prompt Finale (EN):", value=st.session_state['v83_prompt'], height=300)
    
    if st.button("🔥 GENERA COPERTINA HD"):
        if not p_edit:
            st.error("Configura prima la sidebar!")
        else:
            client = replicate.Client(api_token=st.secrets["REPLICATE_API_TOKEN"])
            try:
                with st.spinner("Generazione in corso..."):
                    out = client.run(
                        "black-forest-labs/flux-1.1-pro",
                        input={"prompt": p_edit, "aspect_ratio": "2:3", "output_format": "jpg", "output_quality": 100}
                    )
                    st.session_state['v83_res'] = str(out)
                    st.balloons()
            except Exception as e:
                st.error(f"Errore tecnico: {e}")

with col_r:
    if st.session_state['v83_res']:
        st.image(st.session_state['v83_res'], use_container_width=True)
        st.divider()
        response = requests.get(st.session_state['v83_res'])
        st.download_button(label="📥 Scarica Copertina", data=response.content, file_name="cover.jpg", mime="image/jpeg")
    else:
        st.info("Configura e genera per visualizzare l'anteprima.")
