import streamlit as st
import replicate
import requests
import time
import os
import uuid
from moviepy.editor import VideoFileClip, concatenate_videoclips
from deep_translator import GoogleTranslator

# --- CONFIGURAZIONE UI ---
st.set_page_config(page_title="AI Economy Studio v62", page_icon="💰", layout="wide")

st.markdown("""
    <style>
    [data-testid="sidebar-button"] { display: none !important; }
    [data-testid="stSidebar"] { min-width: 350px !important; background-color: #0d1117; border-right: 1px solid #333; }
    #MainMenu, footer, header, .stAppDeployButton { visibility: hidden; }
    .main { background-color: #0d1117; color: #c9d1d9; }
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #f1c40f 0%, #f39c12 100%);
        color: black; font-size: 1.1rem; font-weight: 800; border-radius: 8px; width: 100%; height: 3.5rem; border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNZIONE MONTAGGIO ---
def merge_videos(urls):
    session_id = str(uuid.uuid4())[:6]
    temp_files, clips = [], []
    output_filename = f"final_video_{session_id}.mp4"
    try:
        for i, url in enumerate(urls):
            path = f"temp_{i}_{session_id}.mp4"
            resp = requests.get(url, timeout=30)
            if resp.status_code == 200:
                with open(path, "wb") as f: f.write(resp.content)
                temp_files.append(path)
                clips.append(VideoFileClip(path))
        
        if clips:
            final = concatenate_videoclips(clips, method="compose")
            final.write_videofile(output_filename, codec="libx264", audio=False, logger=None)
            return output_filename
    except Exception as e:
        st.error(f"Errore montaggio: {e}")
        return None
    finally:
        for c in clips: c.close()
        for f in temp_files: 
            if os.path.exists(f): os.remove(f)

# --- LOGICA SESSIONE ---
if 'ready_p' not in st.session_state: st.session_state['ready_p'] = ""
if 'final_res' not in st.session_state: st.session_state['final_res'] = None

# --- SIDEBAR ---
with st.sidebar:
    st.title("💰 ECONOMY v62")
    st.caption("Engine: CogVideoX (Stabile)")
    mode = st.radio("Seleziona:", ["Video 15s", "Immagine HD"])
    st.divider()
    sub = st.text_input("Soggetto (IT):")
    act = st.text_area("Azione (IT):")
    
    if st.button("🪄 TRADUCI SCRIPT"):
        if sub and act:
            with st.spinner("Traduzione..."):
                full = f"{sub}, {act}, cinematic, highly detailed"
                st.session_state['ready_p'] = GoogleTranslator(source='it', target='en').translate(full)
                st.success("Pronto!")

# --- MAIN ---
st.title(f"🚀 Workstation: {mode}")
c1, c2 = st.columns([1.5, 1])

with c1:
    f_prompt = st.text_area("Prompt Finale (EN):", value=st.session_state['ready_p'], height=150)
    
    if st.button("🔥 AVVIA PRODUZIONE"):
        if not f_prompt:
            st.warning("Traduci lo script!")
        elif "REPLICATE_API_TOKEN" not in st.secrets:
            st.error("Token mancante nei Secrets!")
        else:
            client = replicate.Client(api_token=st.secrets["REPLICATE_API_TOKEN"])
            st.session_state['final_res'] = None
            
            try:
                if mode == "Immagine HD":
                    with st.spinner("Generazione immagine..."):
                        # Usiamo Flux Schnell: economico e non crasha
                        img = client.run("black-forest-labs/flux-schnell", input={"prompt": f_prompt})
                        st.session_state['final_res'] = img[0]
                else:
                    video_urls = []
                    with st.status("🎬 Generazione Clip...", expanded=True) as status:
                        for i in range(3):
                            status.write(f"Produzione clip {i+1}/3...")
                            # CogVideoX-5b: Versione bloccata per evitare errori 404/422
                            res = client.run(
                                "thibaudz/cogvideox-5b:928c084666f2a24c16a3c6d1a91e3e44070a92070c538a08a28f731e8e2c0e",
                                input={"prompt": f"{f_prompt}, segment {i+1}"}
                            )
                            # Controllo se l'output è una lista o stringa
                            video_url = res[0] if isinstance(res, list) else res
                            video_urls.append(video_url)
                            time.sleep(5) # Pausa per evitare throttle
                        
                        status.write("📦 Montaggio finale...")
                        st.session_state['final_res'] = merge_videos(video_urls)
                        if st.session_state['final_res']: st.balloons()
            
            except Exception as e:
                st.error(f"Errore API Replicate: {e}")
                st.info("Verifica il tuo credito su Replicate o riprova tra 1 minuto.")

with c2:
    st.subheader("📺 Anteprima")
    res = st.session_state['final_res']
    if res:
        if mode == "Immagine HD":
            st.image(res)
        else:
            if os.path.exists(str(res)):
                st.video(res)
                with open(res, "rb") as f:
                    st.download_button("📥 Scarica Video", f, "video_15s.mp4")
    else:
        st.info("In attesa...")

st.caption("v62.0 Bulletproof | CogVideoX Locked Version | Sidebar Locked")
