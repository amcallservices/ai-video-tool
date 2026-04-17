import streamlit as st
import replicate
import requests
import time
import os
from moviepy.editor import VideoFileClip, concatenate_videoclips
from deep_translator import GoogleTranslator

# --- CONFIGURAZIONE UI ---
st.set_page_config(page_title="Minimax 15s Ultra-Stitcher", page_icon="🎬", layout="wide")

st.markdown("""
    <style>
    [data-testid="sidebar-button"] { display: none !important; }
    [data-testid="stSidebar"] { min-width: 400px !important; background-color: #0d1117; border-right: 1px solid #333; }
    #MainMenu, footer, header, .stAppDeployButton { visibility: hidden; }
    .main { background-color: #0d1117; }
    div.stButton > button:first-child {
        background: linear-gradient(180deg, #ff4b4b 0%, #8b0000 100%);
        color: white; font-size: 1.3rem; font-weight: 900; height: 5rem; border-radius: 10px; width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGICA DI stitching ---
def stitch_videos(video_urls):
    """Scarica le clip e le unisce in un unico file da 15+ secondi."""
    temp_files = []
    clips = []
    output_path = "final_master_15s.mp4"
    
    try:
        for i, url in enumerate(video_urls):
            fname = f"temp_{i}.mp4"
            with open(fname, "wb") as f:
                f.write(requests.get(url).content)
            temp_files.append(fname)
            clips.append(VideoFileClip(fname))
        
        final_clip = concatenate_videoclips(clips, method="compose")
        final_clip.write_videofile(output_path, codec="libx264", audio=False)
        return output_path
    finally:
        for c in clips: c.close()
        for f in temp_files: 
            if os.path.exists(f): os.remove(f)

# --- SIDEBAR ---
with st.sidebar:
    st.title("🛡️ ULTRA-STITCHER")
    st.info("Questa versione unisce 3 clip da 5s per garantirti 15s totali.")
    
    it_sub = st.text_input("Soggetto (IT):")
    it_act = st.text_area("Azione (IT):")
    
    if st.button("🪄 TRADUCI SCRIPT"):
        ts = GoogleTranslator(source='it', target='en').translate(it_sub)
        ta = GoogleTranslator(source='it', target='en').translate(it_act)
        st.session_state['eng_p'] = f"Cinematic 8k, {ts} {ta}. High quality motion."
        st.success("Pronto!")

# --- MAIN ---
st.title("🚀 Produzione Garantita 15 Secondi")
if 'eng_p' in st.session_state:
    final_p = st.text_area("Script:", value=st.session_state['eng_p'], height=150)
    
    if st.button("🔥 AVVIA PRODUZIONE E UNIONE AUTOMATICA"):
        urls = []
        client = replicate.Client(api_token=st.secrets["REPLICATE_API_TOKEN"])
        
        # Generiamo 3 clip per assicurarci di coprire i 15 secondi
        progress_bar = st.progress(0)
        for i in range(3):
            st.write(f"Generazione parte {i+1}...")
            prediction = client.predictions.create(
                model="minimax/video-01",
                input={"prompt": f"{final_p}, sequence part {i+1}", "video_length": "5s"}
            )
            while prediction.status not in ["succeeded", "failed"]:
                time.sleep(5)
                prediction.reload()
            
            if prediction.status == "succeeded":
                urls.append(prediction.output[0] if isinstance(prediction.output, list) else prediction.output)
            progress_bar.progress((i + 1) / 3)
        
        if len(urls) == 3:
            with st.spinner("📦 Unione delle clip in corso..."):
                final_video = stitch_videos(urls)
                st.session_state['final_v'] = final_video
                st.balloons()

if 'final_v' in st.session_state:
    st.subheader("🎞️ Risultato Finale (Stitched)")
    st.video(st.session_state['final_v'])
    with open(st.session_state['final_v'], "rb") as f:
        st.download_button("📥 Scarica Video Unico 15s", f, "video_finale.mp4")
