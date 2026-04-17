import streamlit as st
import replicate
import requests
import time
import os
import uuid
from moviepy.editor import VideoFileClip, concatenate_videoclips
from deep_translator import GoogleTranslator

# ==============================================================================
# 1. ARCHITETTURA UI & DESIGN (SIDEBAR BLOCCATA)
# ==============================================================================

st.set_page_config(page_title="AI Studio Ultimate v51", page_icon="🎬", layout="wide")

st.markdown("""
    <style>
    /* Rimozione pulsanti e blocco sidebar */
    [data-testid="sidebar-button"] { display: none !important; }
    [data-testid="stSidebar"] {
        min-width: 400px !important;
        background-color: #0d1117;
        border-right: 1px solid #30363d;
    }
    #MainMenu, footer, header, .stAppDeployButton { visibility: hidden; }
    .main { background-color: #0d1117; color: #c9d1d9; }
    
    /* Input Styling */
    .stTextArea textarea, .stTextInput input {
        background-color: #161b22 !important;
        color: #58a6ff !important;
        border: 1px solid #30363d !important;
    }

    /* Pulsante Master */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%);
        color: white; font-size: 1.2rem; font-weight: 800; height: 4.5rem;
        border-radius: 10px; width: 100%; border: none;
        box-shadow: 0 4px 15px rgba(29, 78, 216, 0.3);
    }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 2. LOGICA DI MONTAGGIO (STITCHING)
# ==============================================================================

def stitch_video_clips(urls):
    """Scarica e unisce le clip video in un unico file master."""
    session_id = str(uuid.uuid4())[:6]
    temp_files = []
    clips = []
    output_name = f"master_production_{session_id}.mp4"
    
    try:
        for i, url in enumerate(urls):
            fname = f"clip_{i}_{session_id}.mp4"
            r = requests.get(url, timeout=60)
            if r.status_code == 200:
                with open(fname, "wb") as f:
                    f.write(r.content)
                temp_files.append(fname)
                clips.append(VideoFileClip(fname))
        
        if clips:
            final = concatenate_videoclips(clips, method="compose")
            final.write_videofile(output_name, codec="libx264", audio=False, logger=None)
            return output_name
    except Exception as e:
        st.error(f"Errore montaggio: {e}")
    finally:
        for c in clips: c.close()
        for f in temp_files:
            if os.path.exists(f): os.remove(f)
    return None

# ==============================================================================
# 3. SIDEBAR & CONTROLLI
# ==============================================================================

if 'eng_script' not in st.session_state: st.session_state['eng_script'] = ""
if 'final_output' not in st.session_state: st.session_state['final_output'] = None
if 'is_image_mode' not in st.session_state: st.session_state['is_image_mode'] = False

with st.sidebar:
    st.title("💎 STUDIO v51.0")
    st.caption("Luma & Flux Enterprise Edition")
    st.divider()
    
    # SELETTORE MODALITÀ
    choice = st.radio("Seleziona Output:", ["Video (15s)", "Immagine HD"])
    st.session_state['is_image_mode'] = (choice == "Immagine HD")
    
    st.divider()
    it_sub = st.text_input("Soggetto (IT):")
    it_act = st.text_area("Azione/Dettagli (IT):")
    
    if st.button("🪄 TRADUCI E OTTIMIZZA"):
        if it_sub and it_act:
            with st.spinner("Traduzione..."):
                t = GoogleTranslator(source='it', target='en')
                res = f"{t.translate(it_sub)}, {t.translate(it_act)}, cinematic lighting, 4k, masterpiece."
                st.session_state['eng_script'] = res
                st.success("Prompt Pronto!")

    if st.button("🗑️ Reset"):
        st.session_state.clear()
        st.rerun()

# ==============================================================================
# 4. WORKSTATION DI PRODUZIONE
# ==============================================================================

st.title(f"🚀 Workstation: {choice}")
col_l, col_r = st.columns([1.5, 1])

with col_l:
    prompt_final = st.text_area("Prompt Tecnico (EN):", value=st.session_state['eng_script'], height=150)
    
    if st.button(f"🔥 GENERA {choice.upper()}"):
        if not prompt_final:
            st.error("Traduci lo script prima!")
        elif "REPLICATE_API_TOKEN" not in st.secrets:
            st.error("Manca il Token API nei Secrets!")
        else:
            client = replicate.Client(api_token=st.secrets["REPLICATE_API_TOKEN"])
            st.session_state['final_output'] = None
            
            # --- MODALITÀ IMMAGINE ---
            if st.session_state['is_image_mode']:
                with st.spinner("Rendering Flux..."):
                    try:
                        out = client.run("black-forest-labs/flux-schnell", input={"prompt": prompt_final})
                        st.session_state['final_output'] = str(out[0])
                        st.balloons()
                    except Exception as e:
                        st.error(f"Errore Server Immagine: {e}")
            
            # --- MODALITÀ VIDEO ---
            else:
                urls = []
                with st.status("🎬 Sequenziamento Video...", expanded=True) as status:
                    for i in range(3):
                        clip_done = False
                        retries = 2
                        while not clip_done and retries >= 0:
                            try:
                                status.write(f"Produzione clip {i+1}/3 (Tentativo {3-retries})...")
                                prediction = client.predictions.create(
                                    model="lucataco/animate-diff:be2271c58974859ad77019e44c50d758066e4092070c538a08a28f731e8e2c0e",
                                    input={"prompt": f"{prompt_final}, part {i+1}"}
                                )
                                while prediction.status not in ["succeeded", "failed"]:
                                    time.sleep(5)
                                    prediction.reload()
                                
                                if prediction.status == "succeeded":
                                    urls.append(str(prediction.output))
                                    clip_done = True
                                    if i < 2: 
                                        status.write("⏳ Pausa anti-throttle (15s)...")
                                        time.sleep(15)
                                else:
                                    retries -= 1
                                    time.sleep(10)
                            except Exception as e:
                                retries -= 1
                                time.sleep(10)
                        
                        if not clip_done:
                            st.error(f"Impossibile generare la clip {i+1} dopo 3 tentativi.")
                            break
                    
                    if len(urls) >= 1:
                        status.write("📦 Unione dei segmenti...")
                        st.session_state['final_output'] = stitch_video_clips(urls)
                        if st.session_state['final_output']: st.balloons()

# ==============================================================================
# 5. ANTEPRIMA E DOWNLOAD
# ==============================================================================

with col_r:
    st.subheader("🎞️ Anteprima")
    res = st.session_state['final_output']
    
    if res:
        if st.session_state['is_image_mode']:
            st.image(res)
            st.link_button("📥 Scarica Immagine", res)
        else:
            if os.path.exists(res):
                st.video(res)
                with open(res, "rb") as f:
                    st.download_button("📥 Scarica Video 15s", f, "video_final.mp4")
            else:
                st.error("File video non trovato.")
    else:
        st.info("In attesa di produzione...")

st.caption("v51.0 Ultimate | Flux & Luma Hybrid | Sidebar Locked")
