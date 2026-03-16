import streamlit as st
import feedparser
import google.generativeai as genai
import edge_tts
import asyncio
import aiohttp
import os

# --- CONFIGURAZIONE DELLA PAGINA ---
st.set_page_config(page_title="Notizie Michelone", page_icon="📰", layout="centered")

# --- CONFIGURAZIONE API ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception as e:
    st.error("⚠️ Configura GEMINI_API_KEY nei Secrets di Streamlit!")
    st.stop()

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
        "https://techcrunch.com/feed/"
    ],
    "🔬 Scienza": [
        "https://www.nasa.gov/rss/dyn/breaking_news.rss",
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
    "👦 Ragazzi": [
        "https://www.focusjunior.it/feed/",
        "https://www.focus.it/rss",
        "https://www.ilpost.it/feed/"
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

# --- CREAZIONE BOTTONI A LISTA VERTICALE (OTTIMIZZATI PER LA GUIDA) ---
tema_scelto_dal_bottone = None

# Un semplice loop che crea una bella lista impilata, sicura ed elegante
for categoria in CATEGORIE_NOTIZIE.keys():
    if st.button(categoria, use_container_width=True):
        tema_scelto_dal_bottone = categoria

st.divider()

# --- MOTORE DI GENERAZIONE ---
if tema_scelto_dal_bottone:
    link_da_scaricare = CATEGORIE_NOTIZIE[tema_scelto_dal_bottone]
    
    with st.spinner(f"Sto preparando l'edizione per: {tema_scelto_dal_bottone}..."):
        
        risultati_siti = asyncio.run(raccogli_tutte_le_notizie(link_da_scaricare))
        
        testo_grezzo_notizie = ""
        for feed in risultati_siti:
            if feed and 'entries' in feed:
                for articolo in feed.entries[:7]: 
                    testo_grezzo_notizie += f"- {articolo.title}\n"
        
        # LOGICA SPECIALE PER I RAGAZZI
        if tema_scelto_dal_bottone == "👦 Ragazzi":
            istruzioni_speciali = """
            ATTENZIONE: Questo bollettino è destinato a ragazzi e bambini sotto i 14 anni.
            Devi essere un divulgatore simpatico e rassicurante.
            Ignora ASSOLUTAMENTE notizie di cronaca nera, violenza, guerre crude o politica complessa.
            Scegli solo notizie curiose, scientifiche, storie positive o spiegazioni di eventi importanti adatte alla loro età.
            Usa un linguaggio semplice, divertente ed educativo, dando del "tu" ai ragazzi.
            """
        else:
            istruzioni_speciali = """
            Scrivi in modo chiaro, autorevole e piacevole, pensato per essere letto ad alta voce dalla tua voce artificiale direttamente a Michelone. Evita elenchi puntati o frasi robotiche.
            """

        prompt = f"""
        Sei l'assistente giornalistico personale di Michelone.
        Oggi stai preparando l'edizione esclusiva di "Notizie Michelone" sul tema: "{tema_scelto_dal_bottone}".
        
        Ecco i titoli appena battuti dalle agenzie di stampa:
        {testo_grezzo_notizie}
        
        Il tuo compito è:
        1. Fondere le notizie utili in un unico discorso fluido, avvincente e scorrevole.
        2. {istruzioni_speciali}
        3. Inizia sempre il bollettino dicendo esattamente: "Benvenuto a Notizie Michelone, ecco gli aggiornamenti su..."
        4. Se non ci sono vere notizie, inventa una chiusura simpatica dicendo che per ora la situazione è tranquilla.
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
        
