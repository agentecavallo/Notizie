import streamlit as st
import feedparser
import google.generativeai as genai
import edge_tts
import asyncio
import aiohttp
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

# --- FUNZIONI ASINCRONE (I FATTORINI VELOCI) ---
# 1. Funzione per creare l'audio
async def crea_audio_naturale(testo, nome_file):
    comunicazione = edge_tts.Communicate(testo, "it-IT-ElsaNeural")
    await comunicazione.save(nome_file)

# 2. Funzione per scaricare UN singolo sito (un fattorino)
async def scarica_sito(session, url):
    try:
        # Diamo al massimo 5 secondi, se il sito è bloccato passiamo oltre
        async with session.get(url, timeout=5) as risposta:
            testo_xml = await risposta.text()
            return feedparser.parse(testo_xml)
    except:
        return None # Se c'è un errore col sito, fa finta di niente

# 3. Funzione per mandare tutti i fattorini insieme
async def raccogli_tutte_le_notizie(lista_link):
    async with aiohttp.ClientSession() as session:
        # Prepariamo i 40 fattorini
        lavori = [scarica_sito(session, link) for link in lista_link]
        # Li facciamo partire tutti nello stesso millisecondo
        risultati = await asyncio.gather(*lavori)
        return risultati

st.title("📰 Il Tuo Notiziario Personale AI")
st.write("Scegli un tema. L'IA ascolterà il mondo per te.")

# --- LA TUA MEGA-LISTA DI FONTI RSS ---
fonti_rss = [
    "https://www.ansa.it/sito/ansait_rss.xml",
    "https://www.adnkronos.com/rss.xml",
    "https://www.agi.it/rss",
    "http://xml2.corriereobjects.it/rss/homepage.xml",
    "https://www.repubblica.it/rss/homepage/rss2.0.xml",
    "https://www.lastampa.it/rss/homepage/rss2.0.xml",
    "https://www.ilsole24ore.com/rss/prima-pagina.xml",
    "https://www.ilpost.it/feed/",
    "https://www.ilfattoquotidiano.it/feed/",
    "https://www.rainews.it/rss/tutti",
    "https://tg24.sky.it/rss/edizioni/tg24.xml",
    "https://www.tgcom24.mediaset.it/rss/homepage.xml",
    "https://www.fanpage.it/feed/",
    "https://www.hdblog.it/rss/",
    "https://feeds.hwupgrade.it/rss_news.xml",
    "https://www.wired.it/feed/rss",
    "https://www.punto-informatico.it/feed/",
    "https://www.dday.it/rss",
    "https://www.tomshw.it/feed",
    "https://www.focus.it/rss",
    "https://www.gazzetta.it/rss/home.xml",
    "https://sport.sky.it/rss/sport.xml",
    "https://www.corrieredellosport.it/rss",
    "https://feeds.bbci.co.uk/news/rss.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
    "https://www.theguardian.com/world/rss",
    "https://www.theverge.com/rss/index.xml",
    "https://feeds.arstechnica.com/arstechnica/index",
    "https://techcrunch.com/feed/",
    "https://www.aljazeera.com/xml/rss/all.xml",
    "https://rss.cnn.com/rss/edition.rss",
    "https://www.ft.com/?format=rss",
    "https://www.cnbc.com/id/100003114/device/rss/rss.html",
    "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada",
    "https://www.lemonde.fr/rss/une.xml",
    "https://www.nasa.gov/rss/dyn/breaking_news.rss",
    "https://www.sciencedaily.com/rss/top.xml",
    "https://www.nature.com/nature.rss",
    "https://www.theregister.com/headlines.atom",
    "https://lifehacker.com/feed/rss"
]

temi = [
    "Prima pagina", 
    "Politica italiana", 
    "Politica mondiale", 
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

if st.button("Genera Notizia Magica ✨", use_container_width=True):
    with st.spinner(f"Sto lanciando i fattorini per setacciare il web su: {tema_selezionato}..."):
        
        # 1. Raccogliamo i titoli a velocità tripla!
        risultati_siti = asyncio.run(raccogli_tutte_le_notizie(fonti_rss))
        
        testo_grezzo_notizie = ""
        # 2. Assembliamo i risultati tornati dai fattorini
        for feed in risultati_siti:
            if feed and 'entries' in feed:
                for articolo in feed.entries[:3]: 
                    testo_grezzo_notizie += f"- {articolo.title}\n"
        
        prompt = f"""
        Sei un giornalista esperto e imparziale della radio. Ti fornirò una lunga lista di titoli di notizie appena estratti da decine di agenzie di stampa, con una forte prevalenza italiana.
        Il tuo compito è:
        1. Filtrare le notizie: tieni in considerazione SOLO quelle che riguardano questo specifico tema: "{tema_selezionato}". Ignora il resto.
        2. Tradurre le notizie straniere in italiano.
        3. Scrivere un UNICO articolo fluido e discorsivo, come se dovesse essere letto da uno speaker radiofonico. Dai priorità alle notizie italiane se pertinenti.
        4. Dividi il testo in brevi paragrafi.
        5. Se non trovi nessuna notizia rilevante, scrivi: "Al momento non ci sono notizie di rilievo su questo tema."

        Ecco i titoli grezzi di oggi:
        {testo_grezzo_notizie}
        """

        try:
            risposta = model.generate_content(prompt)
            testo_articolo = risposta.text
            
            st.success("Fatto! L'articolo è pronto.")
            
            st.markdown("### 🎧 Ascolta la Notizia")
            with st.spinner("Sto preparando la voce per la lettura..."):
                testo_pulito = testo_articolo.replace("*", "").replace("#", "")
                file_audio = "notizia_temporanea.mp3"
                asyncio.run(crea_audio_naturale(testo_pulito, file_audio))
                st.audio(file_audio, format='audio/mp3')
            
            st.divider()

            st.markdown("### 🗞️ Il Tuo Articolo da leggere")
            st.write(testo_articolo)
            
        except Exception as e:
            st.error(f"Ops! C'è stato un problema: {e}")
        
