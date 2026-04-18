import streamlit as st
import replicate
import requests
import os
import PyPDF2
from deep_translator import GoogleTranslator

# ==============================================================================
# 1. CONFIGURAZIONE E DESIGN (INVARIATO)
# ==============================================================================
st.set_page_config(page_title="Ebook Designer v87.0 - Narrative Fidelity", page_icon="📕", layout="wide")

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
# 3. KNOWLEDGE BASE PSICOLOGICA E NARRATIVA (INVARIATO)
# ==============================================================================
COLOR_PSYCHOLOGY = """
- ROSSO: Urgenza, Passione, Sopravvivenza.
- BLU: Fiducia, Calma, Logica.
- VERDE: Crescita, Equilibrio, Guarigione.
- VIOLA: Mistero, Spiritualità.
- GIALLO: Ottimismo, Attenzione.
- NERO/GRIGIO: Autorità, Eleganza, Ignoto.
- BIANCO: Purezza, Chiarezza.
"""

NARRATIVE_GUIDE = """
- IDENTIFICA: Il protagonista o l'oggetto iconico centrale.
- AMBIENTAZIONE: Il luogo fisico descritto con più intensità.
- METAFORA VISIVA: Un elemento che riassume il conflitto del libro.
"""

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
    def generate_psychological_concept(text, api_token):
        try:
            client = replicate.Client(api_token=api_token)
            system_prompt = f"""
            Sei un esperto di analisi narrativa e Art Director editoriale. 
            Il tuo compito è analizzare questo estratto e creare un 'Visual Concept' per la copertina che sia profondamente attinente alla storia.
            
            LINEE GUIDA:
            1. Trova il SOGGETTO CENTRALE (personaggio o oggetto chiave) del racconto.
            2. Definisci l'ATMOSFERA (cupa, solare, epica) basandoti sulle parole dell'autore.
            3. Applica la PSICOLOGIA DEL COLORE e gli ARCHETIPI giusti.
            
            ESTRATTO LIBRO: {text[:6000]}
            
            REGOLE DI OUTPUT: 
            Scrivi SOLO la scena visiva in 3 frasi in italiano. 
            Includi dettagli su: Soggetto principale, Sfondo, e palette Colori.
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
# 5. SIDEBAR: COERENZA TESTUALE FEDELE (AGGIORNATO)
# ==============================================================================
with st.sidebar:
    st.title("📕 DESIGNER v87.1")
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
    st.markdown("📄 **Analisi Narrativa & Psicologica**")
    uploaded_pdf = st.file_uploader("Carica il tuo PDF per una profilazione attinente:", type=["pdf"])
    
    if uploaded_pdf is not None:
        if st.button("🧠 Avvia Profilazione Narrativa"):
            if "REPLICATE_API_TOKEN" not in st.secrets:
                st.error("Token mancante!")
            else:
                with st.spinner("Analisi profonda del racconto in corso..."):
                    txt = PDFSemanticPsychologyAnalyzer.extract_text_from_pdf(uploaded_pdf)
                    if txt:
                        ai_scene = PDFSemanticPsychologyAnalyzer.generate_psychological_concept(txt, st.secrets["REPLICATE_API_TOKEN"])
                        if ai_scene:
                            st.session_state['auto_desc'] = ai_scene
                            st.success("Scena attinente al racconto generata!")
    st.markdown('</div>', unsafe_allow_html=True)

    desc_it = st.text_area("3. Scena Visiva (IT):", value=st.session_state['auto_desc'])
    
    # --- INTEGRAZIONE: FEDELTÀ TESTUALE LETTERALE ---
    if st.button("🪄 GENERA ARCHITETTURA"):
        if desc_it:
            with st.spinner("Compilazione..."):
                try:
                    t = GoogleTranslator(source='it', target='en')
                    scene_en = t.translate(desc_it)
                    
                    # Costruzione blocco tipografico con istruzioni di fedeltà assoluta
                    text_layer = ""
                    if use_t and t_val:
                        # Comando rinforzato: 'exact character-for-character string'
                        text_layer += f"The title MUST be the literal string \"{t_val}\", rendered character-for-character with 100% spelling accuracy in 3D font at the {t_pos}. "
                    if use_a and a_val:
                        text_layer += f"The author name MUST be the literal string \"{a_val}\", rendered character-for-character with 100% spelling accuracy at the {a_pos}. "

                    # Prompt Finale con Hard Constraints
                    prompt = (
                        f"TYPOGRAPHY OVERLAY (HIGHEST PRIORITY): {text_layer} "
                        f"BACKGROUND SCENE: A professional ebook cover representing {scene_en}. "
                        f"ARTISTIC STYLE: {ATMOSFERE[genere]} mixed with {MODALITA_RENDERING[tipo_render]}. "
                        f"CRITICAL TYPOGRAPHY RULES: 1. Render the text verbatim as written in the quotes. 2. Do not change any letters or symbols. "
                        f"3. Spelling is mandatory: no character variations. 4. High contrast from background."
                    )
                    st.session_state['v83_prompt'] = prompt
                    st.success("Prompt creato: Fedeltà Caratteri Attiva.")
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
                with st.spinner("Generazione Master in corso..."):
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
