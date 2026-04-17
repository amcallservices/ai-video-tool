import streamlit as st
import replicate
import requests
import time
import os
import uuid
from moviepy.editor import VideoFileClip, concatenate_videoclips
from deep_translator import GoogleTranslator

# --- 1. SETUP UI ---
st.set_page_config(page_title="AI Studio - Low Cost Engine", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    [data-testid="sidebar-button"] { display: none !important; }
    [data-testid="stSidebar"] { min-width: 400px !important; background-color: #0d1117; border-right: 1px solid #30363d; }
    #MainMenu, footer, header, .stAppDeployButton { visibility: hidden; }
    .main { background-color: #0d1117; color: #c9d1d9; }
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #00c853 0%, #b2ff59 100%);
        color: #000; font-size: 1.2rem; font-weight: 800; height: 4.5rem; border-radius: 10px; width: 100%; border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. MONTAGGIO VIDEO ---
def stitch_video_master(urls):
    session_id = str(uuid.uuid4())[:6]
    temp_files, clips = [], []
    out_name = f"final_{session_id}.mp4"
    try:
        for i, url in enumerate(urls):
            fname = f"part_{i}_{session_id}.mp4"
            r = requests.get(url, timeout=60)
            if r.status_code == 200:
                with open(fname, "wb") as f: f.write(r.content)
                temp_files.append(fname)
                clips.append(VideoFileClip(fname))
        if clips:
            final = concatenate_videoclips(clips, method="compose")
            final.write_videofile(out_name, codec="libx264", audio=False, logger=None)
            return out_name
    except Exception as e: st.error(f"Errore montaggio: {e}")
    finally:
        for c in clips: c.close()
        for f in temp_files: 
            if os.path.exists(f): os.remove(f)
    return None

# --- 3. SIDEBAR ---
if 'eng_p' not in st.session_state: st.session_state['eng_p'] = ""
if 'res' not in st.session_state: st.session_state['res'] = None

with st.sidebar:
    st.title("⚡ ECONOMY ENGINE")
    st.caption("Wan-2.1 (Low Cost) & Flux")
    mode = st.radio("Tipo Output:", ["Video (15s)", "Immagine HD"])
    st.divider()
    it_sub = st.text_input("Soggetto (IT):")
    it_act = st.text_area("Azione (IT):")
    if st.button("🪄 TRADUCI"):
        if it_sub and it_act:
            t = GoogleTranslator(source='it', target='en')
            st.session_state['eng_p'] = f"{t.translate(it_sub)}, {t.translate(it_act)}, high quality, cinematic."
            st.success("Prompt Pronto!")

# --- 4. PRODUZIONE ---
st.title(f"🚀 Workstation: {mode}")
col_l, col_r = st.columns([1.5, 1])

with col_l:
    p_final = st.text_area("Script (EN):", value=st.session_state['eng_p'], height=150)
    if st.button("🔥 GENERA"):
        if not p_final: st.error("Traduci lo script!")
        elif "REPLICATE_API_TOKEN" not in st.secrets: st.error("Manca il Token API!")
        else:
            client = replicate.Client(api_token=st.secrets["REPLICATE_API_TOKEN"])
            st.session_state['res'] = None
            
            if mode == "Immagine HD":
                with st.spinner("Flux Rendering..."):
                    try:
                        out = client.run("black-forest-labs/flux-schnell", input={"prompt": p_final})
                        st.session_state['res'] = str(out[0])
                    except Exception as e: st.error(f"Errore: {e}")
            else:
                urls = []
                with st.status("🎬 Produzione Video (Wan-2.1)...", expanded=True) as status:
                    for i in range(3):
                        try:
                            status.write(f"Clip {i+1}/3...")
                            # Wan-2.1 è molto più economico e meno saturo di Luma
                            prediction = client.run(
                                "wan-ai/wan-2.1-t2v-1.3b",
                                input={
                                    "prompt": f"{p_final}, segment {i+1}",
                                    "aspect_ratio": "16:9"
                                }
                            )
                            # Wan restituisce direttamente l'URL o una lista
                            urls.append(str(prediction[0] if isinstance(prediction, list) else prediction))
                            if i < 2: time.sleep(10)
                        except Exception as e:
                            st.error(f"Errore clip {i+1}: {e}")
                            break
                    if len(urls) >= 1:
                        st.session_state['res'] = stitch_video_master(urls)

with col_r:
    st.subheader("🎞️ Anteprima")
    if st.session_state['res']:
        if mode == "Immagine HD":
            st.image(st.session_state['res'])
        else:
            if os.path.exists(st.session_state['res']):
                st.video(st.session_state['res'])
                with open(st.session_state['res'], "rb") as f:
                    st.download_button("📥 Scarica Master", f, "video_15s.mp4")
    else: st.info("In attesa...")
