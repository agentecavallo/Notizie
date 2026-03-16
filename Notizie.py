import streamlit as st
import feedparser
import google.generativeai as genai
import edge_tts
import asyncio
import os

# --- CONFIGURAZIONE DELLA PAGINA ---
st.set_page_config(page_title="Il Mio Notiziario", page_icon="📰", layout="centered")

# --- CONFIGURAZIONE API ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception as e:
    st.error("⚠️ Configura GEMINI_API_KEY nei Secrets di Streamlit!")
    st.stop()

# Motore: Gemini 3.1 Flash-Lite
model = genai.GenerativeModel('gemini-3.1-flash-lite-preview')

# --- FUNZIONE PER LA VOCE NATURALE ---
# edge-tts usa un sistema "asincrono" (fa più cose contemporaneamente),
# quindi dobbiamo creare una piccola funzione apposita.
async def crea_audio_naturale(testo, nome_file):
    # "it-IT-ElsaNeural" è una fantastica voce femminile italiana molto naturale
    comunicazione = edge_tts.Communicate(testo, "it-IT-ElsaNeural")
    await comunicazione.save(nome_file)

st.title("📰 Il Tuo Notiziario Personale AI")
st.write("Scegli un tema. L'Intelligenza Artificiale leggerà le fonti di tutto il mondo, tradurrà e creerà un unico articolo per te.")

# --- LE TUE FONTI RSS ---
fonti_rss = [
    "https://www.ansa.it/sito/ansait_rss.xml",
    "https://www.adnkronos.com/rss.xml",
    "http://xml2.corriereobjects.it/rss/homepage.xml",
    "https://www.ilpost.it/feed/",
    "https://www.hdblog.it/rss/",
    "https://feeds.hwupgrade.it/rss_news.xml",
    "https://www.wired.it/feed/rss",
    "https://feeds.bbci.co.uk/news/rss.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
    "https://www.theguardian.com/world/rss",
    "https://www.theverge.com/rss/index.xml",
    "https://feeds.arstechnica.com/arstechnica/index",
    "https://techcrunch.com/feed/",
    "https://www.nasa.gov/rss/dyn/breaking_news.rss",
    "https://www.sciencedaily.com/rss/top.xml",
    "https://www.nature.com/nature.rss",
    "https://www.theregister.com/headlines.atom",
    "https://lifehacker.com/feed/rss"
]

# --- I TEMI SCELTI DA TE ---
temi = [
    "Prima pagina", 
    "Politico italiano", 
    "Politico mondiale", 
    "Attualità italiana",
    "Sport italiano",
    "Economia mondiale",
    "Novità tecnologiche",
    "Novità scientifiche",
    "Novità mediche", 
    "Musica italiana", 
    "Musica mondiale"
]

tema_selezionato = st.radio("Seleziona il tema che ti interessa:", temi)

st.divider()

# --- IL MOTORE DEL PROGRAMMA ---
if st.button("Genera Notizia Magica ✨", use_container_width=True):
    with st.spinner(f"Sto setacciando il web per: {tema_selezionato}... e scrivendo l'articolo!"):
        
        # 1. Raccogliamo i titoli
        testo_grezzo_notizie = ""
        for link in fonti_rss:
            try:
                feed = feedparser.parse(link)
                for articolo in feed.entries[:5]: 
                    testo_grezzo_notizie += f"- {articolo.title}\n"
            except:
                pass 
        
        # 2. Il Prompt per Gemini
        prompt = f"""
        Sei un giornalista esperto e imparziale della radio. Ti fornirò una lunga lista di titoli di notizie appena estratti da agenzie di stampa.
        Il tuo compito è:
        1. Filtrare le notizie: tieni in considerazione SOLO quelle che riguardano questo specifico tema: "{tema_selezionato}". 
        2. Tradurre tutto in italiano corretto e scorrevole.
        3. Scrivere un UNICO articolo fluido e discorsivo, come se dovesse essere letto da uno speaker radiofonico. Non fare elenchi puntati.
        4. Dividi il testo in brevi paragrafi.
        5. Se non trovi nessuna notizia rilevante, scrivi semplicemente: "Al momento non ci sono notizie di rilievo su questo tema."

        Ecco i titoli grezzi estratti oggi:
        {testo_grezzo_notizie}
        """

        try:
            # 3. Generazione del testo
            risposta = model.generate_content(prompt)
            testo_articolo = risposta.text
            
            st.success("Fatto! L'articolo è pronto.")
            
            # 4. CREAZIONE AUDIO NATURALE (Mostrato in alto!)
            st.markdown("### 🎧 Ascolta la Notizia")
            with st.spinner("Sto preparando la voce per la lettura..."):
                # Pulizia per non far leggere simboli strani alla voce
                testo_pulito = testo_articolo.replace("*", "").replace("#", "")
                
                # Definiamo dove salvare il file audio temporaneo
                file_audio = "notizia_temporanea.mp3"
                
                # Facciamo partire la creazione della voce
                asyncio.run(crea_audio_naturale(testo_pulito, file_audio))
                
                # Mostriamo il player in alto
                st.audio(file_audio, format='audio/mp3')
            
            st.divider()

            # 5. TESTO SCRITTO (Spostato sotto)
            st.markdown("### 🗞️ Il Tuo Articolo da leggere")
            st.write(testo_articolo)
            
        except Exception as e:
            st.error(f"Ops! C'è stato un problema: {e}")
        
