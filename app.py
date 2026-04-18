import streamlit as st
import replicate
import requests
import os
import PyPDF2
from deep_translator import GoogleTranslator

# ==============================================================================
# 1. CONFIGURAZIONE E DESIGN
# ==============================================================================
st.set_page_config(page_title="Ebook Designer v86.1 - 3D Text Edition", page_icon="📕", layout="wide")

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
# 3. KNOWLEDGE BASE PSICOLOGICA (INTEGRAZIONE ENTERPRISE)
# ==============================================================================
# Questo modulo espande drasticamente l'intelligenza dell'app fornendo 
# regole di neuromarketing e psicologia visiva.
COLOR_PSYCHOLOGY = """
- ROSSO: Urgenza, Passione, Pericolo, Sopravvivenza (Ideale per Thriller, Business aggressivo)
- BLU: Fiducia, Calma, Sicurezza, Logica (Ideale per Saggi Scientifici, Manuali Tecnici)
- VERDE: Crescita, Natura, Denaro, Equilibrio, Guarigione (Ideale per Psicologia, Finanza, Meditazione)
- VIOLA: Mistero, Spiritualità, Lusso, Magia (Ideale per Fantasy, Esoterico, Religioso)
- GIALLO: Ottimismo, Attenzione, Follia, Energia (Ideale per Quiz, Saggi provocatori)
- NERO/GRIGIO: Autorità, Eleganza, Paura, Sconosciuto (Ideale per Noir, Thriller psicologici)
- BIANCO: Purezza, Chiarezza, Vuoto, Verità (Ideale per Saggi minimalisti, Biografie)
"""

ARCHETYPES = """
- IL SAGGIO: Simboli (Libri, Gufi, Scale, Luce che filtra). Temi (Verità, Scoperta).
- IL GUERRIERO: Simboli (Armi, Montagne ripide, Tempeste). Temi (Sfida, Vittoria).
- L'AMANTE: Simboli (Fiori, Intrecci, Forme morbide). Temi (Connessione, Sensualità).
- IL MAGO: Simboli (Nebbia, Astri, Geometrie complesse). Temi (Trasformazione, Mistero).
- L'ESPLORATORE: Simboli (Orizzonti, Sentieri, Bussole). Temi (Libertà, Ricerca interiore).
"""

class PDFSemanticPsychologyAnalyzer:
    """
    Motore avanzato per l'estrazione semantica. Analizza il testo non solo per 
    il contenuto, ma per la risonanza emotiva, applicando teorie psicologiche.
    """
    
    @staticmethod
    def extract_text_from_pdf(pdf_file, max_pages=8):
        """Estrae un volume maggiore di testo per un'analisi psicologica più profonda."""
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
        """Invia il testo a Llama-3 con istruzioni di neuromarketing e psicologia."""
        try:
            client = replicate.Client(api_token=api_token)
            
            system_prompt = f"""
            Sei un esperto di psicologia umana, neuromarketing e art direction editoriale.
            Il tuo compito è analizzare l'estratto di questo libro e progettare la scena visiva della copertina.
            
            REGOLE DI ANALISI PSICOLOGICA:
            1. Analizza il senso profondo e il "dolore" o "desiderio" del lettore target.
            2. Seleziona i COLORI dominanti usando la psicologia del colore.
            3. Seleziona un SOGGETTO VISIVO basato sugli archetipi junghiani che risuoni con l'inconscio.
            
            RISORSE:
            {COLOR_PSYCHOLOGY}
            {ARCHETYPES}
            
            ESTRATTO LIBRO: {text[:5000]}
            
            OUTPUT RICHIESTO:
            Scrivi SOLO ed esclusivamente la descrizione della scena (massimo 3 frasi in italiano).
            La descrizione DEVE menzionare i colori scelti, l'atmosfera emotiva e il soggetto visivo. Nessun commento o preambolo.
            """
            
            output = client.run(
                "meta/meta-llama-3-8b-instruct",
                input={"prompt": system_prompt, "max_tokens": 200, "temperature": 0.5}
            )
            return "".join(output)
        except Exception as e:
            st.error(f"Errore nel Motore LLM Psicologico: {e}")
            return None

# ==============================================================================
# 4. MATRICE DEGLI STILI (DINAMICA CON NUOVE CATEGORIE)
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
    st.title("📕 DESIGNER v86.1")
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

    # NUOVO MODULO PDF: ANALISI PSICOLOGICA
    st.markdown('<div class="pdf-uploader-box">', unsafe_allow_html=True)
    st.markdown("📄 **Analisi Psicologica del Libro**")
    uploaded_pdf = st.file_uploader("Carica PDF per estrarre Archetipi e Colori:", type=["pdf"])
    
    if uploaded_pdf is not None:
        if st.button("🧠 Avvia Profilazione IA", help="Analizza il testo con modelli di neuromarketing"):
            if "REPLICATE_API_TOKEN" not in st.secrets:
                st.error("Inserisci il REPLICATE_API_TOKEN nei secrets per usare l'analisi IA.")
            else:
                with st.spinner("Estrazione semantica e mappatura emotiva in corso..."):
                    extracted_text = PDFSemanticPsychologyAnalyzer.extract_text_from_pdf(uploaded_pdf)
                    if extracted_text:
                        ai_scene = PDFSemanticPsychologyAnalyzer.generate_psychological_concept(extracted_text, st.secrets["REPLICATE_API_TOKEN"])
                        if ai_scene:
                            st.session_state['auto_desc'] = ai_scene
                            st.success("Analisi Completata! Scena psicologica generata.")
    st.markdown('</div>', unsafe_allow_html=True)

    desc_it = st.text_area("3. Scena Visiva (IT):", value=st.session_state['auto_desc'], placeholder="Es: Un monaco in cima a una montagna...")
    
    if st.button("🪄 GENERA ARCHITETTURA"):
        if desc_it:
            with st.spinner("Compilazione..."):
                try:
                    t = GoogleTranslator(source='it', target='en')
                    scene_en = t.translate(desc_it)
                    
                    # ------------------------------------------------------------------
                    # INTEGRAZIONE: FORZATURA TESTUALE IN RILIEVO ASSOLUTO
                    # ------------------------------------------------------------------
                    text_block = []
                    if use_t and t_val:
                        text_block.append(
                            f"CRITICAL MANDATE: The exact text \"{t_val}\" MUST be explicitly printed as the main title at the {t_pos}. "
                            f"Use massive, 3D embossed, high-relief typography that physically pops out from the background with clear shadows."
                        )
                    if use_a and a_val:
                        text_block.append(
                            f"CRITICAL MANDATE: The exact text \"{a_val}\" MUST be explicitly printed as the author name at the {a_pos}. "
                            f"Use clear, 3D embossed, high-relief typography."
                        )
                    
                    # Composizione Prompt finale con barriere anti-allucinazione aggiornate
                    prompt = (
                        f"TYPOGRAPHY LAYER (HIGHEST PRIORITY): {' '.join(text_block)} "
                        f"BACKGROUND SCENE: A professional ebook cover representing: {scene_en}. "
                        f"ART DIRECTION: {ATMOSFERE[genere]} combined with {MODALITA_RENDERING[tipo_render]}. "
                        f"STRICT INSTRUCTIONS: 1. You are forbidden from misspelling the title or author. Render the exact characters inside the quotes. "
                        f"2. The typography MUST have a strong 3D embossed relief effect to stand out prominently. "
                        f"3. Ensure maximum color contrast between the background and the text to maintain readability. "
                        f"4. Do not write '{genere}' on the cover."
                    )
                    st.session_state['v83_prompt'] = prompt
                    st.success("Prompt creato con successo! Testi forzati in rilievo.")
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
