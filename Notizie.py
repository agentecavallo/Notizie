import streamlit as st
import feedparser
import google.generativeai as genai
import edge_tts
import asyncio
import aiohttp
import os

# --- CONFIGURAZIONE DELLA PAGINA ---
# Impostiamo il layout "wide" per sfruttare tutto lo schermo del tuo Pixel 8 Pro
st.set_page_config(page_title="Il Mio Notiziario", page_icon="📻", layout="wide")

# --- CONFIGURAZIONE API ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception as e:
    st.error("⚠️ Configura GEMINI_API_KEY nei Secrets di Streamlit!")
    st.stop()

# Motore: Gemini 3.1 Flash-Lite (Super Veloce)
model = genai.GenerativeModel('gemini-3.1-flash-lite-preview')

# --- FUNZIONI ASINCRONE (I FATTORINI VELOCI) ---
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

# --- I TUOI CANALI RADIO (FILTRO INTELLIGENTE) ---
# Adesso ogni tema ha SOLO i suoi siti specifici. Niente sprechi!
CANALI_RADIO = {
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
st.title("📻 Auto-Radio AI")
st.write("Tocca un canale per ascoltare le ultime notizie.")

st.divider()

# --- CREAZIONE DELLA GRIGLIA DI BOTTONI ---
# Estraiamo i nomi dei canali per creare i bottoni
nomi_canali = list(CANALI_RADIO.keys())
tema_scelto_dal_bottone = None

# Creiamo le file da 3 colonne ciascuna
for i in range(0, len(nomi_canali), 3):
    col1, col2, col3 = st.columns(3)
    
    # Bottone Colonna 1
    if i < len(nomi_canali):
        if col1.button(nomi_canali[i], use_container_width=True):
            tema_scelto_dal_bottone = nomi_canali[i]
            
    # Bottone Colonna 2
    if i + 1 < len(nomi_canali):
        if col2.button(nomi_canali[i+1], use_container_width=True):
            tema_scelto_dal_bottone = nomi_canali[i+1]
            
    # Bottone Colonna 3
    if i + 2 < len(nomi_canali):
        if col3.button(nomi_canali[i+2], use_container_width=True):
            tema_scelto_dal_bottone = nomi_canali[i+2]

st.divider()

# --- MOTORE DI GENERAZIONE (Parte solo se premi un bottone) ---
if tema_scelto_dal_bottone:
    # Recuperiamo solo i link giusti per il tema scelto!
    link_da_scaricare = CANALI_RADIO[tema_scelto_dal_bottone]
    
    with st.spinner(f"Sto sintonizzando la radio su {tema_scelto_dal_bottone}..."):
        
        # 1. Lanciamo i fattorini SOLO sui siti selezionati (velocissimo!)
        risultati_siti = asyncio.run(raccogli_tutte_le_notizie(link_da_scaricare))
        
        testo_grezzo_notizie = ""
        # 2. Assembliamo i titoli (Prendiamo fino a 7 articoli dai siti selezionati)
        for feed in risultati_siti:
            if feed and 'entries' in feed:
                for articolo in feed.entries[:7]: 
                    testo_grezzo_notizie += f"- {articolo.title}\n"
        
        prompt = f"""
        Sei il conduttore di un giornale radio di altissimo livello.
        Oggi stai conducendo lo speciale sul tema: "{tema_scelto_dal_bottone}".
        
        Ecco i titoli appena battuti dalle agenzie di stampa:
        {testo_grezzo_notizie}
        
        Il tuo compito è:
        1. Ignorare le notizie fuori tema o palesemente inutili.
        2. Fondere tutto in un unico discorso molto fluido, avvincente e scorrevole.
        3. Scrivi ESATTAMENTE come parleresti al microfono in radio. Evita elenchi puntati o frasi robotiche. Usa un tono professionale ma coinvolgente.
        4. Inizia sempre salutando gli ascoltatori dicendo "Benvenuti allo speciale su..."
        5. Se non ci sono vere notizie, inventa una chiusura simpatica dicendo che per ora la situazione è tranquilla.
        """

        try:
            # 3. Chiediamo a Gemini di scrivere il copione
            risposta = model.generate_content(prompt)
            testo_articolo = risposta.text
            
            # 4. Generiamo l'audio
            st.markdown(f"### 🎧 In onda ora: {tema_scelto_dal_bottone}")
            testo_pulito = testo_articolo.replace("*", "").replace("#", "")
            file_audio = "notizia_temporanea.mp3"
            
            asyncio.run(crea_audio_naturale(testo_pulito, file_audio))
            
            # Mostriamo il player e facciamo in modo che si noti bene!
            st.audio(file_audio, format='audio/mp3')
            
            # Mostriamo il testo sotto
            with st.expander("📝 Leggi il copione radiofonico (se non guidi!)"):
                st.write(testo_articolo)
            
        except Exception as e:
            st.error(f"Ops! C'è stato un problema di trasmissione: {e}")
        
