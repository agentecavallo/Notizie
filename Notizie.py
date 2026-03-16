import streamlit as st
import feedparser
import google.generativeai as genai
import edge_tts
import asyncio
import aiohttp
import os

# --- CONFIGURAZIONE DELLA PAGINA ---
st.set_page_config(page_title="Notizie Michelone", page_icon="📰", layout="wide")

# --- CONFIGURAZIONE API ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception as e:
    st.error("⚠️ Configura GEMINI_API_KEY nei Secrets di Streamlit!")
    st.stop()

# Motore: Gemini 3.1 Flash-Lite
model = genai.GenerativeModel('gemini-3.1-flash-lite-preview')

# --- FUNZIONI ASINCRONE ---
async def crea_audio_naturale(testo, nome_file):
    comunicazione = edge_tts.Communicate(testo, "it-IT-ElsaNeural")
    await comunicazione.save(nome_file)

async def scarica_sito(session, url):
    try:
        async with session.get(url, timeout=5) as risposta:
            testo_xml = await risposta.text()
            return feedparser.parse(testo_xml)
    except:
        return None

async def raccogli_tutte_le_notizie(lista_link):
    async with aiohttp.ClientSession() as session:
        lavori = [scarica_sito(session, link) for link in lista_link]
        risultati = await asyncio.gather(*lavori)
        return risultati

# --- I TEMI DI NOTIZIE MICHELONE ---
CATEGORIE_NOTIZIE = {
    "🌍 Prima Pagina": [
        "https://www.ansa.it/sito/ansait_rss.xml",
        "https://feeds.bbci.co.uk/news/rss.xml",
        "http://xml2.corriereobjects.it/rss/homepage.xml",
        "https://www.ilpost.it/feed/"
    ],
    "🇮🇹 Italia": [
        "https://www.ansa.it/sito/ansait_rss.xml",
        "https://www.repubblica.it/rss/homepage/rss2.0.xml",
        "https://www.ilsole24ore.com/rss/prima-pagina.xml",
        "http://xml2.corriereobjects.it/rss/homepage.xml"
    ],
    "🗺️ Mondo": [
        "https://feeds.bbci.co.uk/news/rss.xml",
        "https://rss.cnn.com/rss/edition.rss",
        "https://www.aljazeera.com/xml/rss/all.xml",
        "https://www.theguardian.com/world/rss"
    ],
    "💼 Economia": [
        "https://www.ilsole24ore.com/rss/economia.xml",
        "https://www.ft.com/?format=rss",
        "https://www.cnbc.com/id/100003114/device/rss/rss.html"
    ],
    "🚀 Tech & AI": [
        "https://www.hdblog.it/rss/",
        "https://www.wired.it/feed/rss",
        "https://www.theverge.com/rss/index.xml",
        "https://techcrunch.com/feed/",
        "https://www.punto-informatico.it/feed/"
    ],
    "🔬 Scienza": [
        "https://www.nasa.gov/rss/dyn/breaking_news.rss",
        "https://www.nature.com/nature.rss",
        "https://www.sciencedaily.com/rss/top.xml",
        "https://www.focus.it/rss"
    ],
    "⚽ Sport": [
        "https://www.gazzetta.it/rss/home.xml",
        "https://sport.sky.it/rss/sport.xml",
        "https://www.corrieredellosport.it/rss"
    ],
    "🦅 S.S. Lazio": [
        "https://www.lalaziosiamonoi.it/rss",
        "https://www.cittaceleste.it/feed/",
        "https://www.laziochannel.it/feed/"
    ],
    "🍿 Intrattenimento": [
        "https://www.ilpost.it/feed/",
        "https://lifehacker.com/feed/rss"
    ],
    "🎵 Musica": [
        "https://www.rollingstone.it/feed/",
        "https://www.billboard.it/feed/"
    ]
}

# --- INTERFACCIA UTENTE ---
st.title("📰 Notizie Michelone")
st.write("Tocca una categoria per generare il tuo bollettino personale.")

st.divider()

# --- CREAZIONE DELLA GRIGLIA DI BOTTONI ---
nomi_categorie = list(CATEGORIE_NOTIZIE.keys())
tema_scelto_dal_bottone = None

for i in range(0, len(nomi_categorie), 3):
    col1, col2, col3 = st.columns(3)
    
    if i < len(nomi_categorie):
        if col1.button(nomi_categorie[i], use_container_width=True):
            tema_scelto_dal_bottone = nomi_categorie[i]
            
    if i + 1 < len(nomi_categorie):
        if col2.button(nomi_categorie[i+1], use_container_width=True):
            tema_scelto_dal_bottone = nomi_categorie[i+1]
            
    if i + 2 < len(nomi_categorie):
        if col3.button(nomi_categorie[i+2], use_container_width=True):
            tema_scelto_dal_bottone = nomi_categorie[i+2]

st.divider()

# --- MOTORE DI GENERAZIONE ---
if tema_scelto_dal_bottone:
    link_da_scaricare = CATEGORIE_NOTIZIE[tema_scelto_dal_bottone]
    
    with st.spinner(f"Sto preparando l'edizione di Notizie Michelone per: {tema_scelto_dal_bottone}..."):
        
        risultati_siti = asyncio.run(raccogli_tutte_le_notizie(link_da_scaricare))
        
        testo_grezzo_notizie = ""
        for feed in risultati_siti:
            if feed and 'entries' in feed:
                for articolo in feed.entries[:7]: 
                    testo_grezzo_notizie += f"- {articolo.title}\n"
        
        prompt = f"""
        Sei l'assistente giornalistico personale di Michelone.
        Oggi stai preparando l'edizione esclusiva di "Notizie Michelone" sul tema: "{tema_scelto_dal_bottone}".
        
        Ecco i titoli appena battuti dalle agenzie di stampa:
        {testo_grezzo_notizie}
        
        Il tuo compito è:
        1. Ignorare le notizie fuori tema o palesemente inutili.
        2. Fondere tutto in un unico discorso molto fluido, avvincente e scorrevole.
        3. Scrivi in modo chiaro e piacevole, pensato per essere letto ad alta voce dalla tua voce artificiale direttamente a Michelone. Evita elenchi puntati o frasi robotiche.
        4. Inizia sempre il bollettino dicendo esattamente: "Benvenuto a Notizie Michelone, ecco gli aggiornamenti su..."
        5. Se non ci sono vere notizie, inventa una chiusura simpatica dicendo a Michelone che per ora la situazione è tranquilla.
        """

        try:
            risposta = model.generate_content(prompt)
            testo_articolo = risposta.text
            
            st.markdown(f"### 🎧 Ascolta Notizie Michelone: {tema_scelto_dal_bottone}")
            testo_pulito = testo_articolo.replace("*", "").replace("#", "")
            file_audio = "notizie_michelone.mp3"
            
            asyncio.run(crea_audio_naturale(testo_pulito, file_audio))
            
            st.audio(file_audio, format='audio/mp3')
            
            with st.expander("📝 Leggi il testo della notizia"):
                st.write(testo_articolo)
            
        except Exception as e:
            st.error(f"Ops! C'è stato un problema di redazione: {e}")
        
