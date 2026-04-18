import streamlit as st
import replicate
import requests
import os
import PyPDF2
from deep_translator import GoogleTranslator

# ==============================================================================
# 1. CONFIGURAZIONE E DESIGN (INVARIATO)
# ==============================================================================
st.set_page_config(page_title="Ebook Designer v86.2 - Precision Text", page_icon="📕", layout="wide")

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
# 3. KNOWLEDGE BASE PSICOLOGICA (INVARIATO)
# ==============================================================================
COLOR_PSYCHOLOGY = """
- ROSSO: Urgenza, Passione, Pericolo (Thriller)
- BLU: Fiducia, Calma, Logica (Saggi)
- VERDE: Crescita, Equilibrio, Guarigione (Psicologia)
- VIOLA: Mistero, Spiritualità (Esoterico)
- GIALLO: Ottimismo, Attenzione (Saggi)
- NERO/GRIGIO: Autorità, Eleganza (Noir)
- BIANCO: Purezza, Chiarezza (Minimalismo)
"""

ARCHETYPES = """
- IL SAGGIO: Verità, Scoperta.
- IL GUERRIERO: Sfida, Vittoria.
- L'AMANTE: Connessione, Sensualità.
- IL MAGO: Trasformazione, Mistero.
- L'ESPLORATORE: Libertà, Ricerca interiore.
"""

class PDFSemanticPsychologyAnalyzer:
    @staticmethod
    def extract_text_from_pdf(pdf_file, max_pages=8):
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
    def generate_psychological_concept(text, api_token):
        try:
            client = replicate.Client(api_token=api_token)
            system_prompt = f"""
            Sei un esperto di psicologia umana e art direction. Analizza il libro e crea la scena visiva.
            ESTRATTO LIBRO: {text[:5000]}
            REGOLE: Scrivi SOLO la scena (massimo 3 frasi in italiano) menzionando colori e atmosfera.
            """
            output = client.run(
                "meta/meta-llama-3-8b-instruct",
                input={"prompt": system_prompt, "max_tokens": 200, "temperature": 0.5}
            )
            return "".join(output)
        except Exception as e:
            st.error(f"Errore Motore LLM: {e}")
            return None

# ==============================================================================
# 4. MATRICE DEGLI STILI (INVARIATO)
# ==============================================================================
MODALITA_RENDERING = {
    "Fotorealistico": "photorealistic, 8k, highly detailed",
    "Illustrazione": "artistic digital illustration, vibrant",
    "3D Render": "octane render, unreal engine 5, 3d depth",
    "Minimalista": "flat design, vector art, minimalist",
    "Vintage": "retro oil painting style, aged paper"
}

ATMOSFERE = {
    "Saggio Scientifico": "clean academic layout",
    "Quiz Scientifico": "dynamic educational layout",
    "Manuale Tecnico": "technical schematic style",
    "Business": "corporate luxury, gold accents",
    "Romanzo Rosa": "dreamy lighting, soft pastel",
    "Thriller": "noir suspense, high contrast",
    "Fantasy": "epic magical atmosphere",
    "Fantascienza": "cyberpunk tech, futuristic",
    "Manuale Psicologico": "zen minimalist balance",
    "Biografia": "classic biography, elegant portrait",
    "Religioso/Teologico": "sacred divine atmosphere",
    "Spirituale/Esoterico": "mystical vibes, occult symbols",
    "Meditazione": "peaceful serenity, zen harmony"
}

# ==============================================================================
# 5. SIDEBAR: CORREZIONE CHIRURGICA TESTO
# ==============================================================================
with st.sidebar:
    st.title("📕 DESIGNER v86.2")
    if st.button("🔄 RESET COMPLETO"): reset_all()
    
    st.divider()
    genere = st.selectbox("1. Atmosfera Editoriale:", list(ATMOSFERE.keys()))
    tipo_render = st.selectbox("2. Stile di Rendering:", list(MODALITA_RENDERING.keys()))
    
    st.divider()
    
    # Checkbox e Input Testuali
    use_t = st.checkbox("Abilita Inserimento Titolo", value=True)
    t_val = st.text_input("Testo Titolo:", "TITOLO ESEMPIO") if use_t else ""
    t_pos = st.selectbox("Posizione Titolo:", ["top", "center", "bottom"]) if use_t else ""

    use_a = st.checkbox("Abilita Inserimento Autore", value=True)
    a_val = st.text_input("Nome Autore:", "AUTORE ESEMPIO") if use_a else ""
    a_pos = st.selectbox("Posizione Autore:", ["top", "center", "bottom"], index=2) if use_a else ""

    st.divider()

    # Modulo PDF
    st.markdown('<div class="pdf-uploader-box">', unsafe_allow_html=True)
    st.markdown("📄 **Analisi Psicologica del Libro**")
    uploaded_pdf = st.file_uploader("Carica PDF:", type=["pdf"])
    
    if uploaded_pdf is not None:
        if st.button("🧠 Avvia Profilazione IA"):
            if "REPLICATE_API_TOKEN" not in st.secrets:
                st.error("Token mancante!")
            else:
                with st.spinner("Analisi in corso..."):
                    txt = PDFSemanticPsychologyAnalyzer.extract_text_from_pdf(uploaded_pdf)
                    if txt:
                        ai_scene = PDFSemanticPsychologyAnalyzer.generate_psychological_concept(txt, st.secrets["REPLICATE_API_TOKEN"])
                        if ai_scene:
                            st.session_state['auto_desc'] = ai_scene
                            st.success("Scena psicologica generata.")
    st.markdown('</div>', unsafe_allow_html=True)

    desc_it = st.text_area("3. Scena Visiva (IT):", value=st.session_state['auto_desc'])
    
    # --- CORREZIONE CHIRURGICA PROMPT ---
    if st.button("🪄 GENERA ARCHITETTURA"):
        if desc_it:
            with st.spinner("Compilazione..."):
                try:
                    t = GoogleTranslator(source='it', target='en')
                    scene_en = t.translate(desc_it)
                    
                    # Costruzione blocco tipografico mandatorio
                    text_layer = ""
                    if use_t and t_val:
                        text_layer += f"The title \"{t_val}\" must be printed in massive, bold, clear 3D font at the {t_pos} of the cover. "
                    if use_a and a_val:
                        text_layer += f"The author name \"{a_val}\" must be clearly printed in a readable font at the {a_pos} of the cover. "

                    # Prompt Finale con Gerarchia Prioritaria
                    # Il testo è la PRIMA cosa che l'IA deve leggere
                    prompt = (
                        f"PRIMARY TEXTUAL OVERLAY: {text_layer} "
                        f"BACKGROUND SCENE: A high-quality professional ebook cover representing {scene_en}. "
                        f"ARTISTIC STYLE: {ATMOSFERE[genere]} mixed with {MODALITA_RENDERING[tipo_render]}. "
                        f"CRITICAL RULES: 1. You MUST render the exact text provided in quotes. 2. High contrast between text and image background. 3. No spelling mistakes. 4. No extra characters."
                    )
                    st.session_state['v83_prompt'] = prompt
                    st.success("Prompt creato: Testo forzato con priorità 1.")
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
