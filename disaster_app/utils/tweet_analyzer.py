import pickle
import spacy
import re
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import subprocess

# Ensure the spaCy model is downloaded
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

sia = SentimentIntensityAnalyzer()


def extract_locations(tweet):
    """Extract potential location mentions from a tweet."""
    # spaCy entity recognition
    doc = nlp(tweet)
    locations = [ent.text for ent in doc.ents if ent.label_ ==
                 "GPE" or ent.label_ == "LOC"]

    # Regular expression patterns for location extraction
    patterns = [
        r"\b\w+(?: city| town| village| state| province| country)\b",
        r"\b\w+(?: mountain| river| lake| ocean| sea)\b",
        r"\b[A-Z][a-z]+, [A-Z]{2}\b"  # US city, state format
    ]

    for pattern in patterns:
        regex_locations = re.findall(pattern, tweet)
        locations.extend(regex_locations)

    return list(set(locations))  # Remove duplicates


# Define disaster keywords
disaster_keywords = {
    # Natural Disasters
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

    # Environmental Disasters
    'water pollution': ['water pollution', 'oil spill', 'marine pollution', 'water contamination'],
    'oil spill': ['oil spill', 'marine pollution', 'petroleum spill', 'crude oil leak'],
    'chemical spill': ['chemical spill', 'hazardous material', 'toxic leak', 'chemical contamination'],
    'nuclear accident': ['nuclear accident', 'radiation leak', 'meltdown', 'nuclear fallout'],

    # Health Disasters
    'pandemic': ['pandemic', 'epidemic', 'outbreak', 'plague', 'infection'],

    # Infrastructure Disasters
    'power outage': ['power outage', 'blackout', 'electricity failure', 'power failure'],
    'building collapse': ['building collapse', 'structural failure', 'collapse', 'crash'],
    'plane crash': ['plane crash', 'aviation disaster', 'aircraft accident', 'airplane crash'],
    'train crash': ['train crash', 'railway accident', 'derailment', 'train wreck'],
    'ship sinking': ['ship sinking', 'maritime disaster', 'shipwreck', 'vessel sinking'],

    # Economic Disasters
    'economic crisis': ['economic crisis', 'recession', 'financial crisis', 'economic downturn'],
    'food shortage': ['food shortage', 'famine', 'starvation', 'hunger'],
    'water shortage': ['water shortage', 'drought', 'water crisis', 'water scarcity'],

    # Other Disasters
    'terrorist attack': ['terrorist attack', 'bombing', 'attack', 'terrorism'],
    'cyber attack': ['cyber attack', 'data breach', 'hacking', 'cybersecurity threat'],
    'heavy rainfall': ['heavy rainfall', 'torrential rain', 'downpour', 'rainstorm', 'heavy rain'],
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


def predict_tweet(tweet):
    """Analyze a tweet to predict disaster-related information."""
    # Load models
    lr_model = pickle.load(open('lr_model.pkl', 'rb'))
    vectorizer = pickle.load(open('vectorizer.pkl', 'rb'))
    st = pickle.load(open('scaler.pkl', 'rb'))

    # Preprocess tweet
    tweet_vectorized = vectorizer.transform([tweet])
    tweet_scaled = st.transform(tweet_vectorized.toarray())

    # Extract locations
    locations = extract_locations(tweet)

    # Make prediction
    prediction = lr_model.predict(tweet_scaled)

    # Determine disaster category
    category = 'Unknown Category'
    for keyword, words in disaster_keywords.items():
        for word in words:
            if word.lower() in tweet.lower():
                category = keyword.capitalize()
                break

    # Sentiment analysis
    sentiment_scores = sia.polarity_scores(tweet)
    sentiment = 'Positive' if sentiment_scores[
        'compound'] >= 0.05 else 'Negative' if sentiment_scores['compound'] <= -0.05 else 'Neutral'

    return {
        'tweet': tweet,
        'is_disaster': prediction[0],
        'location': locations[0] if locations else 'Unknown',
        'category': category,
        'sentiment': sentiment
    }
