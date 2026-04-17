import streamlit as st
import replicate
import requests
import time
import os
import uuid
from moviepy.editor import VideoFileClip, concatenate_videoclips
from deep_translator import GoogleTranslator

# --- CONFIGURAZIONE UI ---
st.set_page_config(page_title="AI Economy Studio", page_icon="💰", layout="wide")

st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #0d1117; border-right: 1px solid #333; }
    .main { background-color: #0d1117; color: #c9d1d9; }
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
        color: white; font-weight: 800; border-radius: 10px; border: none; width: 100%; height: 3.5rem;
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
            path = f"temp_{i}.mp4"
            resp = requests.get(url)
            with open(path, "wb") as f: f.write(resp.content)
            temp_files.append(path)
            clips.append(VideoFileClip(path))
        
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

# --- SIDEBAR ---
with st.sidebar:
    st.title("💰 ECONOMY HUB")
    st.info("Engine: CogVideoX (Video) & Flux (Immagine)")
    mode = st.radio("Cosa vuoi creare?", ["Video 15s (Economy)", "Immagine HD"])
    st.divider()
    soggetto = st.text_input("Soggetto (es: Un gatto astronauta)")
    azione = st.text_area("Cosa fa? (es: Cammina sulla luna)")
    
    prompt_en = ""
    if st.button("🪄 TRADUCI E PREPARA"):
        if soggetto and azione:
            full_it = f"{soggetto}, {azione}, stile cinematografico, alta definizione"
            prompt_en = GoogleTranslator(source='it', target='en').translate(full_it)
            st.session_state['ready_prompt'] = prompt_en
            st.success("Pronto!")

# --- MAIN ---
st.title("🚀 Produzione AI a basso costo")
col1, col2 = st.columns([2, 1])

with col1:
    final_p = st.text_area("Prompt Finale (EN):", value=st.session_state.get('ready_prompt', ''), height=100)
    
    if st.button("🔥 GENERA ORA"):
        if not final_p:
            st.warning("Traduci prima il prompt nella sidebar!")
        else:
            client = replicate.Client(api_token=st.secrets["REPLICATE_API_TOKEN"])
            
            if mode == "Immagine HD":
                with st.spinner("Generazione immagine..."):
                    img_url = client.run("black-forest-labs/flux-schnell", input={"prompt": final_p})
                    st.session_state['result'] = img_url[0]
            else:
                video_urls = []
                with st.status("🎬 Generando 3 clip da 5 secondi...", expanded=True) as status:
                    # CogVideoX-5b è l'opzione più economica ora
                    model = "thibaudz/cogvideox-5b"
                    for i in range(3):
                        status.write(f"Lavoro sulla clip {i+1}/3...")
                        res = client.run(model, input={"prompt": f"{final_p}, sequence part {i+1}", "num_frames": 49})
                        video_urls.append(res)
                        time.sleep(2) # Piccola pausa per stabilità
                    
                    status.write("📦 Unendo i pezzi...")
                    st.session_state['result'] = merge_videos(video_urls)

with col2:
    st.subheader("📺 Anteprima")
    res = st.session_state.get('result')
    if res:
        if mode == "Immagine HD":
            st.image(res)
        else:
            if os.path.exists(str(res)):
                st.video(res)
                with open(res, "rb") as f:
                    st.download_button("📥 Scarica Master", f, "video.mp4")
    else:
        st.info("Il tuo contenuto apparirà qui.")
