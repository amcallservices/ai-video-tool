import streamlit as st
import replicate
import requests
import time
import os
import uuid
from deep_translator import GoogleTranslator

# ==============================================================================
# 1. ARCHITETTURA UI & DESIGN CUSTOM
# ==============================================================================
st.set_page_config(
    page_title="AI Creative Studio v65",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Iniezione CSS per design Dark Premium e Sidebar bloccata
st.markdown("""
    <style>
    /* Reset e Colori Base */
    .main { background-color: #0d1117; color: #c9d1d9; }
    [data-testid="stSidebar"] {
        min-width: 380px !important;
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }
    
    /* Rimozione elementi standard Streamlit */
    #MainMenu, footer, header, [data-testid="sidebar-button"] { visibility: hidden; }
    
    /* Styling Input e Textarea */
    .stTextArea textarea, .stTextInput input {
        background-color: #0d1117 !important;
        color: #58a6ff !important;
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
    }
    
    /* Card Info veritiere */
    .info-card {
        background: #1c2128;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #444c56;
        margin-bottom: 20px;
    }
    
    /* Pulsante Master */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #238636 0%, #2ea043 100%);
        color: white;
        font-size: 1.2rem;
        font-weight: 700;
        height: 4rem;
        border-radius: 10px;
        width: 100%;
        border: none;
        box-shadow: 0 4px 12px rgba(0,0,0,0.5);
        transition: 0.3s;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(46, 160, 67, 0.4);
    }
    
    /* Status Badge */
    .status-badge {
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 2. LOGICA DI SUPPORTO E UTILITY
# ==============================================================================
def check_replicate_token():
    """Verifica la presenza del token nei secrets."""
    if "REPLICATE_API_TOKEN" not in st.secrets:
        st.error("❌ Errore: REPLICATE_API_TOKEN non configurato nei Secrets!")
        return False
    return True

def translate_prompt(soggetto, azione):
    """Traduce e ottimizza il prompt per i modelli AI."""
    try:
        translator = GoogleTranslator(source='it', target='en')
        text_to_translate = f"{soggetto}, {azione}"
        translated = translator.translate(text_to_translate)
        # Aggiunta di tag tecnici per migliorare la resa cinematografica
        optimized = f"Cinematic shot, {translated}, ultra-detailed, 8k resolution, professional lighting, masterpiece."
        return optimized
    except Exception as e:
        st.error(f"Errore traduzione: {e}")
        return None

# ==============================================================================
# 3. SIDEBAR: CONTROLLI E DASHBOARD INFO
# ==============================================================================
if 'final_prompt' not in st.session_state: st.session_state['final_prompt'] = ""
if 'output_media' not in st.session_state: st.session_state['output_media'] = None

with st.sidebar:
    st.title("💎 STUDIO v65.0")
    st.markdown("---")
    
    # Sezione Info Veritiere
    st.markdown("""
        <div class="info-card">
            <h4 style='margin-top:0; color:#58a6ff;'>📊 Info Modelli</h4>
            <p style='font-size:0.9rem;'><b>Video:</b> Minimax Video-01<br>
            <span style='color:#8b949e;'>Stabile, 5 secondi, HD.</span></p>
            <p style='font-size:0.9rem;'><b>Immagine:</b> Flux Schnell<br>
            <span style='color:#8b949e;'>Ultra-veloce, fotorealistico.</span></p>
        </div>
    """, unsafe_allow_html=True)
    
    mode = st.radio("Seleziona Formato Output:", ["Video (5s)", "Immagine HD"])
    st.markdown("---")
    
    st.subheader("📝 Script in Italiano")
    it_soggetto = st.text_input("Soggetto:", placeholder="es. Un astronauta")
    it_azione = st.text_area("Azione/Dettagli:", placeholder="es. Cammina su Marte durante un tramonto rosso")
    
    if st.button("🪄 GENERA PROMPT TECNICO"):
        if it_soggetto and it_azione:
            with st.spinner("Ottimizzazione in corso..."):
                res = translate_prompt(it_soggetto, it_azione)
                if res:
                    st.session_state['final_prompt'] = res
                    st.success("Prompt ottimizzato con successo!")
        else:
            st.warning("Compila entrambi i campi!")

    st.markdown("---")
    if st.button("🗑️ Svuota Sessione"):
        st.session_state.clear()
        st.rerun()

# ==============================================================================
# 4. WORKSTATION CENTRALE (PRODUZIONE)
# ==============================================================================
st.title("🚀 AI Production Workstation")
st.caption("Configurazione: Minimax Video-01 & Flux.1 Schnell")

col_left, col_right = st.columns([1.5, 1])

with col_left:
    prompt_ready = st.text_area(
        "Prompt Finale (Inglese):", 
        value=st.session_state['final_prompt'], 
        height=180,
        help="Puoi modificare manualmente il prompt per aggiungere dettagli tecnici."
    )
    
    if st.button("🔥 AVVIA GENERAZIONE AI"):
        if not prompt_ready:
            st.error("⚠️ Il prompt è vuoto. Usa la sidebar per generarlo o scrivilo manualmente.")
        elif check_replicate_token():
            client = replicate.Client(api_token=st.secrets["REPLICATE_API_TOKEN"])
            st.session_state['output_media'] = None
            
            try:
                if mode == "Immagine HD":
                    with st.spinner("🎨 Rendering Immagine (Flux)..."):
                        # Esecuzione Flux Schnell (Modello ufficiale stabilissimo)
                        output = client.run(
                            "black-forest-labs/flux-schnell",
                            input={"prompt": prompt_ready}
                        )
                        st.session_state['output_media'] = str(output[0])
                        st.balloons()
                else:
                    with st.status("🎬 Produzione Video (Minimax)...", expanded=True) as status:
                        # Minimax Video-01: Il modello più veritiero e funzionale oggi
                        status.write("Inizializzazione server AI...")
                        prediction = client.run(
                            "minimax/video-01",
                            input={"prompt": prompt_ready}
                        )
                        # Minimax restituisce l'URL del video generato
                        st.session_state['output_media'] = str(prediction)
                        status.write("Produzione completata!")
                        st.balloons()
                        
            except Exception as e:
                st.error(f"❌ Errore durante la generazione: {str(e)}")
                st.info("Consiglio: Verifica il credito residuo sul tuo account Replicate.")

# ==============================================================================
# 5. PREVIEW E DOWNLOAD
# ==============================================================================
with col_right:
    st.subheader("🎞️ Anteprima Risultato")
    result = st.session_state['output_media']
    
    if result:
        st.markdown("""<div style='background:#1c2128; padding:10px; border-radius:8px; border:1px solid #30363d;'>""", unsafe_allow_html=True)
        if mode == "Immagine HD":
            st.image(result, use_container_width=True, caption="Generata con Flux.1")
            st.link_button("📥 Scarica Immagine HD", result)
        else:
            st.video(result)
            st.link_button("📥 Scarica Video 5s", result)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        # Placeholder quando non c'è ancora un output
        st.markdown("""
            <div style='height: 300px; border: 2px dashed #30363d; border-radius: 10px; display: flex; align-items: center; justify-content: center; color: #484f58;'>
                In attesa di generazione...
            </div>
        """, unsafe_allow_html=True)

# ==============================================================================
# 6. FOOTER E LOG
# ==============================================================================
st.markdown("---")
f_col1, f_col2, f_col3 = st.columns(3)
with f_col1:
    st.caption("Engine: Replicate API")
with f_col2:
    st.caption("Version: 65.0 Ultimate")
with f_col3:
    st.caption("Status: System Ready")

# Fine del codice
