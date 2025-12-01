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
import plotly.graph_objects as go
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# -----------------------------------------------------------------------------
# 1. Page Configuration & Setup
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Disaster Tweet Analyzer",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# 2. Custom CSS & Theme (Modern Dark/Glassmorphism)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* Global Settings */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Background Gradient */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #f8fafc;
    }
    
    /* Glassmorphism Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .glass-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
        border-color: rgba(255, 255, 255, 0.2);
    }
    
    /* Headings */
    h1, h2, h3 {
        color: #f8fafc !important;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    
    h1 {
        background: linear-gradient(to right, #60a5fa, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem !important;
        padding-bottom: 1rem;
    }
    
    /* Custom Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        border: none;
        padding: 0.6rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
        width: 100%;
    }
    
    .stButton > button:hover {
        background: linear-gradient(90deg, #2563eb 0%, #1d4ed8 100%);
        box-shadow: 0 6px 16px rgba(37, 99, 235, 0.4);
        transform: translateY(-1px);
    }
    
    /* Inputs */
    .stTextArea > div > div > textarea {
        background-color: rgba(30, 41, 59, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        color: #f8fafc;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #60a5fa;
        box-shadow: 0 0 0 2px rgba(96, 165, 250, 0.2);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.95);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Metrics/Stats */
    .stat-card {
        background: rgba(59, 130, 246, 0.1);
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        border: 1px solid rgba(59, 130, 246, 0.2);
    }
    .stat-value {
        font-size: 2rem;
        font-weight: 700;
        color: #60a5fa;
    }
    .stat-label {
        font-size: 0.9rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 4px;
        color: #94a3b8;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(255, 255, 255, 0.05);
        color: #60a5fa;
        border-bottom: 2px solid #60a5fa;
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    ::-webkit-scrollbar-track {
        background: #0f172a;
    }
    ::-webkit-scrollbar-thumb {
        background: #334155;
        border-radius: 5px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #475569;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. Helper Functions & Model Loading
# -----------------------------------------------------------------------------

@st.cache_resource
def download_nltk_data():
    try:
        nltk.data.find('sentiment/vader_lexicon.zip')
    except LookupError:
        nltk.download('vader_lexicon')

download_nltk_data()

@st.cache_resource
def load_spacy_model():
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
        return spacy.load("en_core_web_sm")

nlp = load_spacy_model()

@st.cache_resource
def load_sia():
    return SentimentIntensityAnalyzer()

sia = load_sia()

@st.cache_resource
def load_models():
    lr_model = pickle.load(open('lr_model.pkl', 'rb'))
    vectorizer = pickle.load(open('vectorizer.pkl', 'rb'))
    scaler = pickle.load(open('scaler.pkl', 'rb'))
    return lr_model, vectorizer, scaler

lr_model, vectorizer, scaler = load_models()

disaster_keywords = {
    'earthquake': ['earthquake', 'quake', 'tremor', 'seismic', 'aftershock', 'ground shaking'],
    'flood': ['flood', 'flooding', 'inundation', 'deluge', 'flash flood', 'overflow'],
    'fire': ['wildfire', 'fire', 'blaze', 'inferno', 'forest fire', 'brush fire'],
    'storm': ['hurricane', 'typhoon', 'cyclone', 'storm', 'tornado', 'blizzard', 'gale'],
    'accident': ['crash', 'collision', 'derailment', 'wreck', 'accident', 'collapse'],
    'terrorism': ['terrorist', 'bombing', 'attack', 'explosion', 'blast'],
    'health': ['pandemic', 'epidemic', 'outbreak', 'virus', 'infection'],
    'other': ['crisis', 'emergency', 'disaster', 'calamity', 'catastrophe']
}

def extract_locations(tweet):
    doc = nlp(tweet)
    locations = [ent.text for ent in doc.ents if ent.label_ in ["GPE", "LOC"]]
    # Simple regex fallback for common patterns
    patterns = [r"\\b[A-Z][a-z]+, [A-Z]{2}\\b"] # Simplified for demo
    for pattern in patterns:
        locations.extend(re.findall(pattern, tweet))
    return list(set(locations))

def predict_tweet(tweet):
    tweet_vectorized = vectorizer.transform([tweet])
    tweet_scaled = scaler.transform(tweet_vectorized.toarray())
    locations = extract_locations(tweet)
    prediction = lr_model.predict(tweet_scaled)
    
    # Keyword matching for category
    category = 'General Emergency'
    found_keywords = []
    for cat, keywords in disaster_keywords.items():
        if any(k in tweet.lower() for k in keywords):
            category = cat.capitalize()
            found_keywords.append(cat)
            break # Take the first match for simplicity
            
    sentiment_scores = sia.polarity_scores(tweet)
    compound = sentiment_scores['compound']
    sentiment = 'Positive' if compound >= 0.05 else 'Negative' if compound <= -0.05 else 'Neutral'
    
    # Handle prediction output (can be string 'Disaster'/'Safe' or int 1/0)
    pred_val = prediction[0]
    is_disaster = 1 if (str(pred_val).lower() == 'disaster' or pred_val == 1 or str(pred_val) == '1') else 0
    
    return {
        'tweet': tweet,
        'is_disaster': is_disaster,
        'location': locations[0] if locations else None,
        'category': category,
        'sentiment': sentiment,
        'confidence': abs(compound) # Using sentiment intensity as a proxy for "impact" for visualization
    }

@st.cache_data
def get_coordinates(location_name):
    geolocator = Nominatim(user_agent="disaster_tweet_analyzer_v2")
    try:
        location = geolocator.geocode(location_name)
        if location:
            return location.latitude, location.longitude
    except (GeocoderTimedOut, Exception):
        return None
    return None

# -----------------------------------------------------------------------------
# 4. UI Layout
# -----------------------------------------------------------------------------

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/3d-fluency/94/siren.png", width=60)
    st.title("Settings")
    
    st.markdown("### ⚙️ Preferences")
    auto_process = st.checkbox("Auto-process Input", value=True)
    show_map = st.checkbox("Show Map Visualization", value=True)
    
    st.markdown("### 🕒 Recent Activity")
    if "history" not in st.session_state:
        st.session_state.history = []
    
    if st.session_state.history:
        for i, item in enumerate(reversed(st.session_state.history[-5:])):
            status_icon = "🔴" if item['is_disaster'] else "🟢"
            st.caption(f"{status_icon} {item['tweet'][:30]}...")
    else:
        st.caption("No recent activity.")
        
    st.divider()
    st.markdown("Made with ❤️ by Team 3")

# Main Content
st.markdown('<div style="text-align: center; margin-bottom: 2rem;"><h1>🚨 Disaster Tweet Analyzer</h1><p style="font-size: 1.2rem; color: #94a3b8;">Real-time AI Analysis for Disaster Detection & Classification</p></div>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🔍 Single Analysis", "📂 Batch Analysis"])

# --- Tab 1: Single Analysis ---
with tab1:
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("Input Tweet")
        tweet_input = st.text_area("Enter text to analyze", height=120, placeholder="e.g., 'Massive earthquake just hit the coast of Japan! Tsunami warning issued.'", label_visibility="collapsed")
        
        analyze_btn = st.button("Analyze Tweet", type="primary")
        st.markdown('</div>', unsafe_allow_html=True)
        
        if analyze_btn or (auto_process and tweet_input):
            if tweet_input:
                with st.spinner("Analyzing..."):
                    result = predict_tweet(tweet_input)
                    # Only append if it's a new unique tweet or explicit button press to avoid dups on rerun
                    if not st.session_state.history or st.session_state.history[-1]['tweet'] != result['tweet']:
                         st.session_state.history.append(result)
                
                # Result Cards
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.subheader("Analysis Results")
                
                r_c1, r_c2, r_c3 = st.columns(3)
                
                with r_c1:
                    status_color = "#ef4444" if result['is_disaster'] else "#22c55e"
                    status_text = "DISASTER" if result['is_disaster'] else "SAFE"
                    st.markdown(f"""
                        <div class="stat-card" style="border-color: {status_color}; background: {status_color}10;">
                            <div class="stat-value" style="color: {status_color}">{status_text}</div>
                            <div class="stat-label">Classification</div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                with r_c2:
                    sent_color = "#ef4444" if result['sentiment'] == 'Negative' else "#22c55e" if result['sentiment'] == 'Positive' else "#94a3b8"
                    st.markdown(f"""
                        <div class="stat-card">
                            <div class="stat-value" style="color: {sent_color}">{result['sentiment']}</div>
                            <div class="stat-label">Sentiment</div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                with r_c3:
                    st.markdown(f"""
                        <div class="stat-card">
                            <div class="stat-value" style="color: #f59e0b; font-size: 1.5rem; line-height: 2.4rem;">{result['category']}</div>
                            <div class="stat-label">Category</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)

            elif analyze_btn:
                st.warning("Please enter some text first.")

    with col2:
        # Quick Stats & Map
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("Session Stats")
        
        total = len(st.session_state.history)
        disasters = sum(1 for x in st.session_state.history if x['is_disaster'])
        
        m1, m2 = st.columns(2)
        m1.metric("Total Analyzed", total)
        m2.metric("Disasters Found", disasters, delta=f"{disasters/total*100:.1f}%" if total > 0 else None, delta_color="inverse")
        st.markdown('</div>', unsafe_allow_html=True)
        
        if 'result' in locals() and result.get('location') and show_map:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.subheader("📍 Location")
            st.write(f"Detected: **{result['location']}**")
            coords = get_coordinates(result['location'])
            if coords:
                st.map(pd.DataFrame({'lat': [coords[0]], 'lon': [coords[1]]}), zoom=4, use_container_width=True)
            else:
                st.info("Location found but could not be placed on map.")
            st.markdown('</div>', unsafe_allow_html=True)

# --- Tab 2: Batch Analysis ---
with tab2:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 📤 Bulk Upload")
    st.markdown("Upload a CSV file containing a `tweet` or `text` column.")
    uploaded_file = st.file_uploader("Choose CSV", type="csv", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        if 'tweet' in df.columns or 'text' in df.columns:
            col_name = 'tweet' if 'tweet' in df.columns else 'text'
            
            if st.button("Process Batch", type="primary"):
                with st.spinner("Processing batch data..."):
                    results = []
                    progress_bar = st.progress(0)
                    for idx, text in enumerate(df[col_name]):
                        results.append(predict_tweet(str(text)))
                        progress_bar.progress((idx + 1) / len(df))
                    
                    results_df = pd.DataFrame(results)
                    
                    # Dashboard
                    st.markdown("### 📊 Batch Report")
                    
                    # Top Row: Charts
                    c1, c2 = st.columns(2)
                    
                    with c1:
                        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                        fig_pie = px.pie(results_df, names='is_disaster', title='Disaster Distribution',
                                       color_discrete_map={0: '#22c55e', 1: '#ef4444'},
                                       hole=0.4)
                        fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#f8fafc")
                        st.plotly_chart(fig_pie, use_container_width=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                    with c2:
                        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                        fig_bar = px.bar(results_df['sentiment'].value_counts(), title='Sentiment Analysis',
                                       color_discrete_sequence=['#3b82f6'])
                        fig_bar.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#f8fafc")
                        st.plotly_chart(fig_bar, use_container_width=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Word Cloud
                    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                    st.subheader("Word Cloud")
                    text_combined = " ".join(results_df['tweet'])
                    wordcloud = WordCloud(width=800, height=300, background_color='#1e293b', colormap='Blues').generate(text_combined)
                    fig_wc, ax = plt.subplots(figsize=(10, 5))
                    ax.imshow(wordcloud, interpolation='bilinear')
                    ax.axis("off")
                    fig_wc.patch.set_alpha(0) # Transparent figure background
                    st.pyplot(fig_wc)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Data Table
                    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                    st.subheader("Detailed Data")
                    st.dataframe(results_df, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.error("CSV must contain 'tweet' or 'text' column.")

