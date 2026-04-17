import streamlit as st
import replicate
import requests
import time
from deep_translator import GoogleTranslator

# --- CONFIGURAZIONE UI ---
st.set_page_config(page_title="AI Video Studio - Sequence Editor", layout="wide")

st.markdown("""
    <style>
    [data-testid="sidebar-button"] { display: none !important; }
    [data-testid="stSidebar"] { min-width: 450px !important; background-color: #0d1117; }
    .main { background-color: #0d1117; }
    div.stButton > button:first-child {
        background: linear-gradient(180deg, #ff4b4b 0%, #8b0000 100%);
        color: white; font-weight: 800; height: 4rem; width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# --- MOTORE TRADUZIONE ---
def translate_it(text):
    if not text: return ""
    return GoogleTranslator(source='it', target='en').translate(text)

# --- SESSION STATE PER TIMELINE ---
if 'timeline' not in st.session_state: st.session_state['timeline'] = []
if 'current_prompt' not in st.session_state: st.session_state['current_prompt'] = ""

# --- SIDEBAR: REGIA E SEQUENZE ---
with st.sidebar:
    st.title("🎬 SEQUENCE DIRECTOR")
    st.write("Crea clip separate da montare insieme per superare i 15 secondi.")
    
    st.divider()
    durata = st.select_slider("Durata Clip (sec):", options=[6, 10, 15], value=10)
    
    st.subheader("📝 Nuova Scena")
    it_s = st.text_input("Soggetto:", placeholder="Es: Astronauta")
    it_a = st.text_area("Azione Scena:", placeholder="Es: Cammina verso la base spaziale")
    
    if st.button("🪄 GENERA E AGGIUNGI ALLA TIMELINE"):
        if it_s and it_a:
            with st.spinner("Traduzione tecnica..."):
                eng_s = translate_it(it_s)
                eng_a = translate_it(it_a)
                # Costruzione prompt tecnico
                prompt = f"Professional cinematic shot of {eng_s}, {eng_a}. 8k, highly detailed, smooth motion for {durata}s."
                st.session_state['current_prompt'] = prompt
                st.success("Scena pronta e tradotta!")
        else:
            st.warning("Inserisci i dettagli della scena.")

    if st.button("🗑️ Svuota Timeline"):
        st.session_state['timeline'] = []
        st.rerun()

# --- MAIN: WORKSTATION ---
st.title("🚀 Timeline di Produzione")
st.info("Genera le clip una alla volta. Una volta scaricate tutte, potrai unirle nel tuo editor preferito per creare un video lungo.")

col_edit, col_timeline = st.columns([2, 1])

with col_edit:
    st.subheader("🎥 Preview Prompt Corrente")
    final_p = st.text_area("Script per Replicate:", value=st.session_state['current_prompt'], height=150)
    
    if st.button("🔥 GENERA QUESTA CLIP"):
        if not final_p:
            st.error("Nessun prompt pronto.")
        else:
            try:
                client = replicate.Client(api_token=st.secrets["REPLICATE_API_TOKEN"])
                with st.status("🎬 Rendering in corso...", expanded=True) as status:
                    prediction = client.predictions.create(
                        model="minimax/video-01",
                        input={"prompt": final_p, "video_length": f"{durata}s"}
                    )
                    while prediction.status not in ["succeeded", "failed", "canceled"]:
                        time.sleep(10)
                        prediction.reload()
                    
                    if prediction.status == "succeeded":
                        url = prediction.output if isinstance(prediction.output, str) else prediction.output[0]
                        st.video(url)
                        st.session_state['timeline'].append({"url": url, "prompt": final_p})
                        st.success("Clip aggiunta alla timeline!")
            except Exception as e:
                st.error(f"Errore: {e}")

with col_timeline:
    st.subheader("🎞️ La tua Timeline")
    if not st.session_state['timeline']:
        st.write("Nessuna clip generata.")
    else:
        for i, clip in enumerate(st.session_state['timeline']):
            st.write(f"**Clip {i+1}:** {clip['prompt'][:30]}...")
            st.video(clip['url'])
            st.download_button(f"📥 Scarica Clip {i+1}", requests.get(clip['url']).content, f"clip_{i+1}.mp4")

st.divider()
st.caption("v21.0 - Professional Sequence Engine | Sidebar Locked")
