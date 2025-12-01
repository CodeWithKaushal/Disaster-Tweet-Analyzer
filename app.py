import streamlit as st
import pickle
import spacy
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import re
import subprocess
import sys
import pandas as pd
import plotly.express as px
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Page configuration
st.set_page_config(
    page_title="Disaster Tweet Analyzer",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern UI
st.markdown("""
<style>
    .reportview-container {
        background: #f0f2f6;
    }
    .main {
        background: #ffffff;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    h1 {
        color: #1f2937;
    }
    .stButton>button {
        background-color: #3b82f6;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }
    .stButton>button:hover {
        background-color: #2563eb;
    }
</style>
""", unsafe_allow_html=True)

# Download necessary NLTK data
@st.cache_resource
def download_nltk_data():
    try:
        nltk.data.find('sentiment/vader_lexicon.zip')
    except LookupError:
        nltk.download('vader_lexicon')

download_nltk_data()

# Load SpaCy model
@st.cache_resource
def load_spacy_model():
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
        return spacy.load("en_core_web_sm")

nlp = load_spacy_model()

# Load Sentiment Analyzer
@st.cache_resource
def load_sia():
    return SentimentIntensityAnalyzer()

sia = load_sia()

# Load Machine Learning Models
@st.cache_resource
def load_models():
    lr_model = pickle.load(open('lr_model.pkl', 'rb'))
    vectorizer = pickle.load(open('vectorizer.pkl', 'rb'))
    scaler = pickle.load(open('scaler.pkl', 'rb'))
    return lr_model, vectorizer, scaler

lr_model, vectorizer, scaler = load_models()

# Disaster Keywords
disaster_keywords = {
    'earthquake': ['earthquake', 'quake', 'tremor', 'seismic', 'aftershock', 'quake swarm', 'ground shaking', 'temblor'],
    'flood': ['flood', 'flooding', 'inundation', 'deluge', 'flash flood', 'overflow', 'torrential rain', 'rainstorm'],
    'drought': ['drought', 'dry spell', 'water scarcity', 'water shortage', 'aridification', 'desiccation'],
    'landslide': ['landslide', 'mudslide', 'rockslide', 'avalanche', 'rockfall', 'mudflow', 'landslip'],
    'wildfire': ['wildfire', 'fire', 'blaze', 'inferno', 'forest fire', 'brush fire', 'bushfire'],
    'hurricane': ['hurricane', 'typhoon', 'cyclone', 'storm surge', 'tropical storm', 'severe storm'],
    'tornado': ['tornado', 'twister', 'whirlwind', 'funnel cloud', 'rotating storm'],
    'storm': ['storm', 'thunderstorm', 'gale', 'tempest', 'squall', 'windstorm'],
    'tsunami': ['tsunami', 'tidal wave', 'seismic sea wave', 'ocean surge'],
    'volcanic eruption': ['volcano', 'eruption', 'lava flow', 'pyroclastic flow', 'volcanic ash'],
    'heatwave': ['heatwave', 'heat wave', 'temperature rise', 'warm spell', 'hot spell'],
    'blizzard': ['blizzard', 'snowstorm', 'ice storm', 'snowsquall', 'winter storm'],
    'ice storm': ['ice storm', 'freezing rain', 'glaze', 'black ice'],
    'dust storm': ['dust storm', 'sandstorm', 'haboob', 'dust devil'],
    'fog': ['fog', 'smog', 'haze', 'mist'],
    'avalanche': ['avalanche', 'snowslide', 'rockslide', 'landslide'],
    'cyclone': ['cyclone', 'tropical cyclone', 'low pressure', 'depression'],
    'flash flood': ['flash flood', 'sudden flood', 'torrential rain', 'rapid flooding'],
    'water pollution': ['water pollution', 'oil spill', 'marine pollution', 'water contamination'],
    'oil spill': ['oil spill', 'marine pollution', 'petroleum spill', 'crude oil leak'],
    'chemical spill': ['chemical spill', 'hazardous material', 'toxic leak', 'chemical contamination'],
    'nuclear accident': ['nuclear accident', 'radiation leak', 'meltdown', 'nuclear fallout'],
    'pandemic': ['pandemic', 'epidemic', 'outbreak', 'plague', 'infection'],
    'power outage': ['power outage', 'blackout', 'electricity failure', 'power failure'],
    'building collapse': ['building collapse', 'structural failure', 'collapse', 'crash'],
    'plane crash': ['plane crash', 'aviation disaster', 'aircraft accident', 'airplane crash'],
    'train crash': ['train crash', 'railway accident', 'derailment', 'train wreck'],
    'ship sinking': ['ship sinking', 'maritime disaster', 'shipwreck', 'vessel sinking'],
    'economic crisis': ['economic crisis', 'recession', 'financial crisis', 'economic downturn'],
    'food shortage': ['food shortage', 'famine', 'starvation', 'hunger'],
    'water shortage': ['water shortage', 'drought', 'water crisis', 'water scarcity'],
    'terrorist attack': ['terrorist attack', 'bombing', 'attack', 'terrorism'],
    'cyber attack': ['cyber attack', 'data breach', 'hacking', 'cybersecurity threat'],
    'heavy rainfall': ['heavy rainfall', 'torrential rain', 'downpour', 'rainstorm','heavy rain'],
    'low pressure': ['low pressure', 'depression', 'storm system', 'atmospheric pressure'],
    'thunderstorm': ['thunderstorm', 'electrical storm', 'lightning storm', 'thunder'],
    'gale': ['gale', 'strong wind', 'gust', 'windstorm'],
    'hail storm': ['hail storm', 'hail', 'ice pellets', 'sleet'],
    'sandstorm': ['sandstorm', 'dust storm', 'haboob', 'dust devil', 'sandstorm surge'],
    'smog': ['smog', 'air pollution', 'haze', 'fog', 'atmospheric pollution'],
    'heat stress': ['heat stress', 'heat exhaustion', 'heat stroke', 'hyperthermia'],
    'cold wave': ['cold wave', 'cold snap', 'chill', 'freezing temperatures'],
    'windstorm': ['windstorm', 'gale', 'storm', 'strong winds', 'gusts'],
    'winter storm': ['winter storm', 'blizzard', 'snowstorm', 'ice storm', 'freezing rain'],
    'tropical storm': ['tropical storm', 'cyclone', 'hurricane', 'typhoon', 'severe storm'],
    'ice jam': ['ice jam', 'ice blockage', 'river ice', 'frozen river'],
    'fog bank': ['fog bank', 'thick fog', 'dense fog', 'foggy conditions'],
    'snow avalanche': ['snow avalanche', 'snowslide', 'snowslip', 'avalanche'],
    'mudflow': ['mudflow', 'mudslide', 'mud avalanche', 'lahar'],
    'rockfall': ['rockfall', 'rockslide', 'boulder fall', 'stonefall'],
    'forest fire': ['forest fire', 'wildfire', 'brush fire', 'bushfire'],
    'brush fire': ['brush fire', 'bushfire', 'grass fire', 'wildfire'],
    'wildland fire': ['wildland fire', 'wildfire', 'forest fire', 'brush fire'],
    'tsunami warning': ['tsunami warning', 'tsunami alert', 'seismic sea wave warning'],
    'flash flood warning': ['flash flood warning', 'flood warning', 'rapid flooding warning'],
    'severe thunderstorm warning': ['severe thunderstorm warning', 'thunderstorm alert', 'tornado warning'],
    'tornado warning': ['tornado warning', 'tornado alert', 'twister warning'],
    'hurricane warning': ['hurricane warning', 'hurricane alert', 'tropical storm warning'],
    'blizzard warning': ['blizzard warning', 'blizzard alert', 'winter storm warning'],
    'ice storm warning': ['ice storm warning', 'ice alert', 'freezing rain warning'],
    'flood warning': ['flood warning', 'flood alert', 'overflow warning'],
    'drought warning': ['drought warning', 'drought alert', 'water scarcity warning'],
    'heat wave warning': ['heat wave warning', 'heat alert', 'temperature rise warning'],
    'cold wave warning': ['cold wave warning', 'cold alert', 'freezing temperatures warning'],
    'windstorm warning': ['windstorm warning', 'wind alert', 'gale warning'],
    'smog warning': ['smog warning', 'air pollution alert', 'haze warning'],
    'fog warning': ['fog warning', 'fog alert', 'thick fog warning']
}

def extract_locations(tweet):
    doc = nlp(tweet)
    locations = [ent.text for ent in doc.ents if ent.label_ == "GPE" or ent.label_ == "LOC"]
    patterns = [
        r"\b\w+(?: city| town| village| state| province| country)\b",
        r"\b\w+(?: mountain| river| lake| ocean| sea)\b",
        r"\b[A-Z][a-z]+, [A-Z]{2}\b"
    ]
    for pattern in patterns:
        regex_locations = re.findall(pattern, tweet)
        locations.extend(regex_locations)
    return list(set(locations))

def predict_tweet(tweet):
    tweet_vectorized = vectorizer.transform([tweet])
    tweet_scaled = scaler.transform(tweet_vectorized.toarray())
    locations = extract_locations(tweet)
    prediction = lr_model.predict(tweet_scaled)
    category = 'Unknown Category'
    for keyword, words in disaster_keywords.items():
       for word in words:
           if word.lower() in tweet.lower():
               category = keyword.capitalize()
               break
    sentiment_scores = sia.polarity_scores(tweet)
    sentiment = 'Positive' if sentiment_scores['compound'] >= 0.05 else 'Negative' if sentiment_scores['compound'] <= -0.05 else 'Neutral'
    return {
        'tweet': tweet,
        'is_disaster': prediction[0],
        'location': locations[0] if locations else None,
        'category': category,
        'sentiment': sentiment
    }

@st.cache_data
def get_coordinates(location_name):
    geolocator = Nominatim(user_agent="disaster_tweet_analyzer")
    try:
        location = geolocator.geocode(location_name)
        if location:
            return location.latitude, location.longitude
    except (GeocoderTimedOut, Exception):
        return None
    return None

# Sidebar
with st.sidebar:
    st.title("🛠️ Settings")
    st.markdown("Configure your analysis preferences.")
    
    if "history" not in st.session_state:
        st.session_state.history = []
    
    if st.session_state.history:
        st.subheader("Recent Activity")
        for i, item in enumerate(st.session_state.history[-5:]):
            st.text(f"{i+1}. {item['tweet'][:20]}...")
            
    st.divider()
    st.info("Disaster Tweet Analyzer v2.0")

# Main Content
st.title("🚨 Disaster Tweet Analyzer")
st.markdown("### Real-time AI Analysis for Disaster Detection")

tab1, tab2 = st.tabs(["🔍 Single Analysis", "📂 Batch Analysis"])

with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        tweet_input = st.text_area("Enter Tweet", height=150, placeholder="Type a tweet here... (e.g., 'Major flooding in downtown Miami')")
        if st.button("Analyze Tweet", type="primary", use_container_width=True):
            if tweet_input:
                with st.spinner("Processing..."):
                    result = predict_tweet(tweet_input)
                    st.session_state.history.append(result)
                
                # Results
                st.divider()
                r_col1, r_col2, r_col3 = st.columns(3)
                
                with r_col1:
                    st.markdown("#### Status")
                    if result['is_disaster'] == 1:
                        st.error("⚠️ DISASTER")
                    else:
                        st.success("✅ SAFE")
                
                with r_col2:
                    st.markdown("#### Sentiment")
                    color = "red" if result['sentiment'] == 'Negative' else "green" if result['sentiment'] == 'Positive' else "gray"
                    st.markdown(f":{color}[**{result['sentiment']}**]")
                
                with r_col3:
                    st.markdown("#### Category")
                    st.info(result['category'])
                
                if result['location']:
                    st.markdown("#### 📍 Location Detected")
                    st.write(f"**{result['location']}**")
                    coords = get_coordinates(result['location'])
                    if coords:
                        st.map(pd.DataFrame({'lat': [coords[0]], 'lon': [coords[1]]}))
                    else:
                        st.warning("Could not geocode location for map.")
            else:
                st.warning("Please enter text to analyze.")
    
    with col2:
        st.markdown("### Quick Stats")
        st.metric("Total Analyzed", len(st.session_state.history))
        disasters = sum(1 for x in st.session_state.history if x['is_disaster'] == 1)
        st.metric("Disasters Detected", disasters)

with tab2:
    st.markdown("Upload a CSV file containing tweets to analyze them in bulk.")
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        if 'tweet' in df.columns or 'text' in df.columns:
            col_name = 'tweet' if 'tweet' in df.columns else 'text'
            
            if st.button("Analyze Batch"):
                with st.spinner("Analyzing batch..."):
                    results = []
                    for text in df[col_name]:
                        results.append(predict_tweet(str(text)))
                    
                    results_df = pd.DataFrame(results)
                    st.dataframe(results_df)
                    
                    # Visualizations
                    st.divider()
                    st.subheader("📊 Analysis Report")
                    
                    v_col1, v_col2 = st.columns(2)
                    
                    with v_col1:
                        st.markdown("#### Disaster Distribution")
                        fig_pie = px.pie(results_df, names='is_disaster', title='Disaster vs Non-Disaster', 
                                         color_discrete_map={0: 'lightgreen', 1: 'red'},
                                         labels={'is_disaster': 'Is Disaster'})
                        st.plotly_chart(fig_pie, use_container_width=True)
                    
                    with v_col2:
                        st.markdown("#### Sentiment Distribution")
                        fig_bar = px.bar(results_df['sentiment'].value_counts(), title='Sentiment Count')
                        st.plotly_chart(fig_bar, use_container_width=True)
                    
                    # Word Cloud
                    st.markdown("#### Word Cloud")
                    text_combined = " ".join(results_df['tweet'])
                    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text_combined)
                    fig_wc, ax = plt.subplots()
                    ax.imshow(wordcloud, interpolation='bilinear')
                    ax.axis("off")
                    st.pyplot(fig_wc)
                    
                    # Map
                    st.markdown("#### 🌍 Global Impact Map")
                    locations_df = results_df[results_df['location'].notna()]
                    if not locations_df.empty:
                        with st.spinner("Geocoding locations for map... (this may take a while)"):
                            # Simple caching for this session to avoid re-geocoding same places
                            loc_coords = []
                            for loc in locations_df['location'].unique():
                                coords = get_coordinates(loc)
                                if coords:
                                    loc_coords.append({'location': loc, 'lat': coords[0], 'lon': coords[1]})
                            
                            map_data = pd.DataFrame(loc_coords)
                            if not map_data.empty:
                                st.map(map_data)
                            else:
                                st.warning("No valid coordinates found for mapping.")
                    else:
                        st.info("No locations detected in the batch.")
        else:
            st.error("CSV must contain a 'tweet' or 'text' column.")
