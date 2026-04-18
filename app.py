import streamlit as st
import replicate
import requests
import os
import PyPDF2
from deep_translator import GoogleTranslator

# ==============================================================================
# 1. CONFIGURAZIONE E DESIGN
# ==============================================================================
st.set_page_config(page_title="Ebook Designer v85 - PDF AI Engine", page_icon="📕", layout="wide")

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
    .pdf-uploader-box { border: 2px dashed #007bff; padding: 10px; border-radius: 8px; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 2. LOGICA RESET E SESSIONE
# ==============================================================================
if 'v83_prompt' not in st.session_state: st.session_state['v83_prompt'] = ""
if 'v83_res' not in st.session_state: st.session_state['v83_res'] = None
if 'auto_desc' not in st.session_state: st.session_state['auto_desc'] = ""

def reset_all():
    for key in st.session_state.keys():
        del st.session_state[key]
    st.rerun()

# ==============================================================================
# 3. MOTORE DI ESTRAZIONE SEMANTICA PDF (NUOVO MODULO)
# ==============================================================================
class PDFSemanticAnalyzer:
    """
    Classe dedicata all'estrapolazione del senso logico di un libro tramite PDF
    e generazione di una scena visiva utilizzando un LLM testuale su Replicate.
    """
    
    @staticmethod
    def extract_text_from_pdf(pdf_file, max_pages=5):
        """Estrae il testo dalle prime pagine del PDF per capire il contesto."""
        try:
            reader = PyPDF2.PdfReader(pdf_file)
            text_content = ""
            # Leggiamo solo le prime 'max_pages' per non sovraccaricare il token limit dell'LLM
            limit = min(max_pages, len(reader.pages))
            for i in range(limit):
                page = reader.pages[i]
                text_content += page.extract_text() + " "
            return text_content
        except Exception as e:
            st.error(f"Errore nella lettura del PDF: {e}")
            return None

    @staticmethod
    def generate_visual_concept(text, api_token):
        """Invia il testo estratto a Llama-3 per estrapolare la scena della copertina."""
        try:
            client = replicate.Client(api_token=api_token)
            # Prompt per Llama 3: chiediamo di fare il critico letterario e art director
            system_prompt = (
                "Sei un art director editoriale. Leggi l'estratto di questo libro "
                "e scrivi SOLO una breve scena visiva (massimo 2 frasi, in italiano) "
                "perfetta per la copertina di questo libro. Non aggiungere saluti o commenti. "
                f"Estratto libro: {text[:4000]}" # Limitiamo a 4000 caratteri per sicurezza
            )
            
            # Utilizziamo Llama 3 su Replicate per analizzare il testo
            output = client.run(
                "meta/meta-llama-3-8b-instruct",
                input={
                    "prompt": system_prompt,
                    "max_tokens": 150,
                    "temperature": 0.7
                }
            )
            return "".join(output)
        except Exception as e:
            st.error(f"Errore nel Motore LLM: {e}")
            return None

# ==============================================================================
# 4. MATRICE DEGLI STILI 
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
# 5. SIDEBAR: PERSONALIZZAZIONE TOTALE E ANALISI PDF
# ==============================================================================
with st.sidebar:
    st.title("📕 DESIGNER v85")
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
    
    # NUOVO MODULO: UPLOAD PDF E ANALISI
    st.markdown('<div class="pdf-uploader-box">', unsafe_allow_html=True)
    st.markdown("📄 **Analisi Semantica del Libro**")
    uploaded_pdf = st.file_uploader("Carica il PDF per autocompilare la scena:", type=["pdf"])
    
    if uploaded_pdf is not None:
        if st.button("🧠 Analizza PDF", help="Usa l'IA per estrapolare il senso del libro"):
            if "REPLICATE_API_TOKEN" not in st.secrets:
                st.error("Inserisci il REPLICATE_API_TOKEN nei secrets per usare l'analisi IA.")
            else:
                with st.spinner("Lettura del manoscritto e analisi semantica in corso..."):
                    # Estrazione Testo
                    extracted_text = PDFSemanticAnalyzer.extract_text_from_pdf(uploaded_pdf)
                    if extracted_text:
                        # Generazione Scena
                        ai_scene = PDFSemanticAnalyzer.generate_visual_concept(extracted_text, st.secrets["REPLICATE_API_TOKEN"])
                        if ai_scene:
                            st.session_state['auto_desc'] = ai_scene
                            st.success("Analisi completata! Scena generata.")
    st.markdown('</div>', unsafe_allow_html=True)

    # L'utente può usare la scena del PDF o scriverla a mano
    desc_it = st.text_area("3. Scena Visiva (IT):", value=st.session_state['auto_desc'], placeholder="Es: Un monaco in cima a una montagna...")
    
    if st.button("🪄 GENERA ARCHITETTURA"):
        if desc_it:
            with st.spinner("Compilazione..."):
                try:
                    t = GoogleTranslator(source='it', target='en')
                    scene_en = t.translate(desc_it)
                    
                    # CORREZIONE TIPOGRAFICA
                    text_block = []
                    if use_t and t_val:
                        text_block.append(f"The cover must display the exact text \"{t_val}\" clearly as the main title at the {t_pos}.")
                    if use_a and a_val:
                        text_block.append(f"The cover must display the exact author name \"{a_val}\" clearly at the {a_pos}.")
                    
                    # Composizione Prompt finale
                    prompt = (
                        f"TYPOGRAPHY OVERLAY: {' '.join(text_block)} "
                        f"BACKGROUND: A professional ebook cover with {scene_en}. "
                        f"ART STYLE: {ATMOSFERE[genere]} combined with {MODALITA_RENDERING[tipo_render]}. "
                        f"MANDATORY RULES: 1. Render the text exactly as written in quotes. 2. No extra characters or invented letters. 3. High contrast between text and background. 4. Do not write the word '{genere}' on the image."
                    )
                    st.session_state['v83_prompt'] = prompt
                    st.success("Prompt creato con successo!")
                except Exception as e:
                    st.error(f"Errore traduzione: {e}")

# ==============================================================================
# 6. WORKSTATION GENERAZIONE
# ==============================================================================
st.title("🎨 Custom Creative Workstation")
col_l, col_r = st.columns([1.2, 1])

with col_l:
    st.subheader("📝 Prompt Configurator")
    p_edit = st.text_area("Prompt Finale per l'IA (EN):", value=st.session_state['v83_prompt'], height=300)
    
    if st.button("🔥 GENERA COPERTINA HD"):
        if not p_edit:
            st.error("Per favore, configura prima l'architettura nella sidebar a sinistra!")
        else:
            if "REPLICATE_API_TOKEN" not in st.secrets:
                st.error("Errore: REPLICATE_API_TOKEN non trovato nei Secrets di Streamlit.")
            else:
                client = replicate.Client(api_token=st.secrets["REPLICATE_API_TOKEN"])
                try:
                    with st.spinner("L'IA sta dipingendo il tuo capolavoro... attendi qualche secondo."):
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
                    st.error(f"Errore tecnico durante la generazione: {e}")

with col_r:
    st.subheader("🖼️ Anteprima Risultato")
    if st.session_state['v83_res']:
        st.image(st.session_state['v83_res'], use_container_width=True)
        st.divider()
        try:
            response = requests.get(st.session_state['v83_res'])
            st.download_button(
                label="📥 Scarica Copertina in Alta Risoluzione",
                data=response.content,
                file_name="ebook_cover_ai.jpg",
                mime="image/jpeg"
            )
        except:
            st.warning("Impossibile scaricare l'immagine al momento.")
    else:
        st.info("Configura i parametri nella sidebar e clicca su 'Genera Copertina HD' per visualizzare l'anteprima.")
