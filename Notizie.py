import streamlit as st
import feedparser
import google.generativeai as genai

# --- CONFIGURAZIONE DELLA PAGINA ---
st.set_page_config(page_title="Il Mio Notiziario", page_icon="📰", layout="centered")

# --- CONFIGURAZIONE API ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception as e:
    st.error("⚠️ Configura GEMINI_API_KEY nei Secrets di Streamlit!")
    st.stop() # Ferma il programma se manca la chiave

# Motore AGGIORNATO: Gemini 3.1 Flash-Lite (Super veloce, limiti più alti)
model = genai.GenerativeModel('gemini-3.1-flash-lite-preview')

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
    with st.spinner(f"Sto setacciando il web per: {tema_selezionato}... e chiedendo a Gemini 3.1 di scrivere l'articolo!"):
        
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
        Sei un giornalista esperto e imparziale. Ti fornirò una lunga lista di titoli di notizie appena estratti da agenzie di stampa mondiali.
        Il tuo compito è:
        1. Filtrare le notizie: tieni in considerazione SOLO quelle che riguardano questo specifico tema: "{tema_selezionato}". Ignora categoricamente tutte le altre.
        2. Tradurre tutto in italiano corretto e scorrevole.
        3. Fondere le informazioni: non farmi un elenco dei titoli, ma scrivi un UNICO articolo coeso e ben leggibile che riassuma cosa sta succedendo nel mondo riguardo al tema scelto.
        4. Dividi il testo in brevi paragrafi per facilitare la lettura da smartphone.
        5. Se non trovi nessuna notizia rilevante per il tema scelto nella lista fornita, scrivi semplicemente: "Al momento non ci sono notizie di rilievo su questo tema dalle fonti selezionate."

        Ecco i titoli grezzi estratti oggi:
        {testo_grezzo_notizie}
        """

        # 3. Chiediamo a Gemini di generare la risposta
        try:
            risposta = model.generate_content(prompt)
            st.success("Fatto! Ecco il tuo riassunto:")
            
            st.markdown("### 🗞️ Il Tuo Articolo")
            st.write(risposta.text)
            
        except Exception as e:
            st.error(f"Ops! C'è stato un problema con l'Intelligenza Artificiale: {e}")
        
