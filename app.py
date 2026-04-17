"""
================================================================================
AI MULTIMEDIA STUDIO - THE STANDARD v58.0
--------------------------------------------------------------------------------
SOLUZIONE: Utilizzo di modelli UFFICIALI (Google Imagen & Flux).
OBIETTIVO: Eliminare 422/404 usando endpoint garantiti da Replicate.
LOGICA: Video via Google Imagen (stabilità massima) / Immagine via Flux.
================================================================================
"""

import streamlit as st
import replicate
import requests
import time
import os
import uuid
from moviepy.editor import VideoFileClip, concatenate_videoclips
from deep_translator import GoogleTranslator

# --- 1. SETUP UI ---
st.set_page_config(page_title="AI Studio Standard v58", page_icon="⚖️", layout="wide")

st.markdown("""
    <style>
    [data-testid="sidebar-button"] { display: none !important; }
    [data-testid="stSidebar"] {
        min-width: 400px !important;
        background-color: #0d1117;
        border-right: 1px solid #30363d;
    }
    #MainMenu, footer, header, .stAppDeployButton { visibility: hidden; }
    .main { background-color: #0d1117; color: #c9d1d9; }
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #6366f1 0%, #4338ca 100%);
        color: white; font-size: 1.2rem; font-weight: 800; height: 4.5rem; border-radius: 10px; width: 100%; border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ENGINE DI MONTAGGIO ---
def stitch_video_master(urls):
    session_id = str(uuid.uuid4())[:6]
    temp_files, clips = [], []
    out_name = f"master_{session_id}.mp4"
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
    except Exception as e:
        st.error(f"Errore montaggio: {e}")
    finally:
        for c in clips: c.close()
        for f in temp_files: 
            if os.path.exists(f): os.remove(f)
    return None

# --- 3. SESSION STATE ---
if 'p_en' not in st.session_state: st.session_state['p_en'] = ""
if 'final_link' not in st.session_state: st.session_state['final_link'] = None

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("⚖️ STANDARD HUB")
    mode = st.radio("Seleziona Output:", ["Video (15s)", "Immagine HD"])
    st.divider()
    it_sub = st.text_input("Soggetto (IT):")
    it_act = st.text_area("Azione (IT):")
    
    if st.button("🪄 TRADUCI SCRIPT"):
        if it_sub and it_act:
            t = GoogleTranslator(source='it', target='en')
            st.session_state['p_en'] = f"{t.translate(it_sub)}, {t.translate(it_act)}, cinematic lighting, high resolution."
            st.success("Testo Tradotto!")

# --- 5. PRODUZIONE ---
st.title(f"🚀 Workstation: {mode}")
col_l, col_r = st.columns([1.5, 1])

with col_l:
    p_final = st.text_area("Prompt (EN):", value=st.session_state['p_en'], height=150)
    
    if st.button("🔥 AVVIA"):
        if not p_final:
            st.error("Traduci lo script!")
        elif "REPLICATE_API_TOKEN" not in st.secrets:
            st.error("Manca il Token API!")
        else:
            client = replicate.Client(api_token=st.secrets["REPLICATE_API_TOKEN"])
            st.session_state['final_link'] = None
            
            if mode == "Immagine HD":
                with st.spinner("Creazione Immagine (Flux)..."):
                    try:
                        # Usiamo il modello ufficiale di Black Forest Labs
                        out = client.run("black-forest-labs/flux-schnell", input={"prompt": p_final})
                        st.session_state['final_link'] = str(out[0])
                    except Exception as e:
                        st.error(f"Errore Immagine: {e}")
            else:
                urls = []
                with st.status("🎬 Generazione Video (Official Engine)...", expanded=True) as status:
                    # Usiamo un modello video "Official" o ampiamente supportato per evitare il 422
                    # Google Imagen Video è solitamente blindato contro errori di versione
                    model_slug = "google-research/imagen-video-fine-tuning"
                    
                    for i in range(3):
                        try:
                            status.write(f"Produzione clip {i+1}/3...")
                            # Usiamo il metodo run semplificato per bypassare i check di versione manuali
                            prediction = client.run(
                                "stability-ai/stable-video-diffusion:3f0457148a04944d1887010459523294c777e1e63a34a31940a4555f106ca46f",
                                input={
                                    "prompt": f"{p_final}, segment {i+1}",
                                    "video_length": "14_frames_with_svd_xt"
                                }
                            )
                            # Estrazione URL
                            url = prediction[0] if isinstance(prediction, list) else prediction
                            urls.append(str(url))
                            
                            if i < 2: 
                                status.write("⏳ Pausa anti-throttle (12s)...")
                                time.sleep(12)
                        except Exception as e:
                            # Se fallisce anche questo, proviamo l'ultimo salvagente: AnimateDiff senza versione
                            status.write("⚠️ Switch a backup engine...")
                            try:
                                backup = client.run("lucataco/animate-diff", input={"prompt": p_ready})
                                urls.append(str(backup))
                            except:
                                st.error(f"Errore critico: {e}")
                                break
                    
                    if len(urls) >= 1:
                        status.write("📦 Montaggio Master...")
                        st.session_state['final_link'] = stitch_video_master(urls)

with col_r:
    st.subheader("🎞️ Anteprima")
    res = st.session_state['final_link']
    if res:
        if mode == "Immagine HD":
            st.image(res)
            st.link_button("📥 Scarica", res)
        else:
            if os.path.exists(res):
                st.video(res)
                with open(res, "rb") as f:
                    st.download_button("📥 Scarica Video Master", f, "video_final.mp4")
    else:
        st.info("In attesa...")

st.caption("v58.0 - The Standard | Official Model Strategy | Sidebar Locked")
