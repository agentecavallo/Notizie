import streamlit as st
import feedparser

# --- CONFIGURAZIONE DELLA PAGINA ---
# Impostiamo l'app per essere vista bene da cellulare
st.set_page_config(page_title="Il Mio Notiziario", page_icon="📰", layout="centered")

st.title("📰 Il Tuo Notiziario Personale")
st.write("Scegli un tema e scopri cosa succede nel mondo.")

# --- LE TUE FONTI RSS ---
# Qui salviamo i link ai feed RSS dei siti che hai scelto
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
    "https://www.sciencedaily.com/rss/top.xml"
    # (Nota: ne ho inseriti alcuni, gli altri li aggiungeremo man mano per non appesantire il codice ora)
]

# --- I TEMI SCELTI DA TE ---
temi = [
    "Prima pagina italiana", 
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

# --- INTERFACCIA UTENTE (I BOTTONI) ---
# Usiamo i "pills" o un menu a tendina/radio che su telefono sono comodissimi da tappare
tema_selezionato = st.radio("Seleziona il tema che ti interessa:", temi)

st.divider() # Una linea per separare

# --- IL MOTORE DEL PROGRAMMA ---
if st.button("Genera Notizia 🚀", use_container_width=True):
    # Quando l'utente preme il bottone grande, il programma parte
    st.info(f"Sto raccogliendo le notizie per il tema: **{tema_selezionato}**...")
    
    # 1. Raccogliamo tutte le notizie (solo i titoli per ora)
    tutte_le_notizie = []
    for link in fonti_rss:
        feed = feedparser.parse(link)
        for articolo in feed.entries[:3]: # Prendiamo solo i primi 3 per fonte per fare veloce
            tutte_le_notizie.append(articolo.title)
    
    st.success("Notizie raccolte! Ora l'Intelligenza Artificiale le leggerebbe e farebbe il riassunto.")
    
    # 2. IL POSTO DELL'INTELLIGENZA ARTIFICIALE (Placeholder)
    st.markdown("### 📝 Il Grande Riassunto Unico")
    st.write(f"*Qui, in futuro, apparirà il testo unico scritto dall'AI, tradotto in italiano, che parla solo di {tema_selezionato}, usando le informazioni prese da ANSA, NYT, The Verge, ecc.*")
    
    # Mostriamo cosa vede il programma dietro le quinte
    with st.expander("Curioso di vedere i titoli grezzi che l'AI dovrà leggere?"):
        for notizia in tutte_le_notizie[:10]: # Ne mostriamo solo 10 di esempio
            st.write(f"- {notizia}")

