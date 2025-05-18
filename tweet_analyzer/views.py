from django.shortcuts import render

# Create your views here.
import json
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import re
import spacy
import pickle
import os
import joblib
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure the NLTK data is downloaded
try:
    nltk.download('vader_lexicon')
except Exception as e:
    logger.error(f"Error downloading NLTK data: {e}")

# Load the spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    # If the model isn't installed, download it
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")
except Exception as e:
    logger.error(f"Error loading spaCy model: {e}")
    nlp = None

# Sentiment analyzer
try:
    sia = SentimentIntensityAnalyzer()
except Exception as e:
    logger.error(f"Error initializing SentimentIntensityAnalyzer: {e}")
    sia = None

# Load models
BASE_DIR = settings.BASE_DIR
try:
    vectorizer = pickle.load(
        open(os.path.join(BASE_DIR, 'vectorizer.pkl'), 'rb'))
    scaler = pickle.load(open(os.path.join(BASE_DIR, 'scaler.pkl'), 'rb'))
    lr_model = pickle.load(open(os.path.join(BASE_DIR, 'lr_model.pkl'), 'rb'))
    rf_pipeline_model = joblib.load(os.path.join(
        BASE_DIR, 'rf_pipeline_model_bert_only.joblib'))
except Exception as e:
    logger.error(f"Error loading models: {e}")
    vectorizer, scaler, lr_model, rf_pipeline_model = None, None, None, None

# Define disaster keywords (copied from your original app.py)
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
    # Human-Caused Disasters
    'explosion': ['explosion', 'blast', 'detonation', 'bomb', 'bombing', 'explosive'],
    'chemical spill': ['chemical spill', 'toxic release', 'hazardous materials', 'hazmat', 'chemical leak'],
    'oil spill': ['oil spill', 'oil leak', 'oil slick', 'petroleum spill', 'crude oil discharge'],
    'nuclear accident': ['nuclear accident', 'radiation leak', 'radioactive release', 'nuclear meltdown'],
    'fire': ['building fire', 'structure fire', 'house fire', 'apartment fire', 'blaze'],
    'plane crash': ['plane crash', 'aircraft crash', 'air disaster', 'flight crash', 'aviation accident'],
    'train derailment': ['train derailment', 'train crash', 'train accident', 'derailment', 'rail accident'],
    'mass shooting': ['mass shooting', 'active shooter', 'gunman', 'shooting', 'gun violence'],
    'terrorist attack': ['terrorist attack', 'terrorism', 'terror attack', 'bombing', 'terrorist'],
    'cyber attack': ['cyber attack', 'cyber security breach', 'data breach', 'ransomware', 'computer virus'],
    # Health Disasters
    'pandemic': ['pandemic', 'epidemic', 'outbreak', 'disease spread', 'virus outbreak', 'contagion'],
    'food poisoning': ['food poisoning', 'foodborne illness', 'contaminated food', 'food contamination'],
    'water contamination': ['water contamination', 'polluted water', 'tainted water', 'drinking water crisis']
}


def extract_locations(tweet):
    """Extract location information from a tweet"""
    if nlp is None:
        return []

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


def identify_disasters(text):
    """Identify disaster types from text"""
    text_lower = text.lower()
    found_disasters = {}

    for disaster_type, keywords in disaster_keywords.items():
        for keyword in keywords:
            if keyword.lower() in text_lower:
                if disaster_type in found_disasters:
                    found_disasters[disaster_type].append(keyword)
                else:
                    found_disasters[disaster_type] = [keyword]

    return found_disasters


def analyze_sentiment(text):
    """Analyze sentiment of the text"""
    if sia is None:
        return {"positive": 0, "negative": 0, "neutral": 0, "compound": 0}

    sentiment = sia.polarity_scores(text)
    return sentiment


def predict_disaster(text):
    """Predict if the text is about a disaster"""
    if vectorizer is None or scaler is None or lr_model is None:
        return {"prediction": "Error loading models", "probability": 0}

    try:
        # Vectorize the text
        features = vectorizer.transform([text])
        # Scale the features
        scaled_features = scaler.transform(features.toarray())
        # Make prediction
        prediction = lr_model.predict(scaled_features)[0]
        probability = lr_model.predict_proba(scaled_features)[0][1]

        result = {
            "prediction": "Disaster" if prediction == 1 else "Not a Disaster",
            "probability": float(probability)
        }
        return result
    except Exception as e:
        logger.error(f"Error in predict_disaster: {e}")
        return {"prediction": "Error in prediction", "probability": 0}

# View functions


def index(request):
    """Home page view"""
    return render(request, 'django_index.html')


def about_us(request):
    """About Us page view"""
    return render(request, 'about-us_django.html')


def model_insight(request):
    """Model Insight page view"""
    return render(request, 'model-insight_django.html')


def motivation(request):
    """Motivation page view"""
    return render(request, 'motivation.html')


def team(request):
    """Team page view"""
    return render(request, 'team_new.html')


def feedback(request):
    """Feedback form view"""
    return render(request, 'feedback_new.html')


def feedback_submitted(request):
    """Feedback submission confirmation view"""
    return render(request, 'feedback_submitted.html')


@csrf_exempt
def analyze_tweet(request):
    """API endpoint for tweet analysis"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            tweet_text = data.get('tweet', '')

            if not tweet_text:
                return JsonResponse({"error": "No tweet text provided"}, status=400)

            # Perform analysis
            prediction_result = predict_disaster(tweet_text)
            sentiment_result = analyze_sentiment(tweet_text)
            disaster_types = identify_disasters(tweet_text)
            locations = extract_locations(tweet_text)

            response = {
                "prediction": prediction_result,
                "sentiment": sentiment_result,
                "disaster_types": disaster_types,
                "locations": locations
            }

            return JsonResponse(response)

        except Exception as e:
            logger.error(f"Error in analyze_tweet: {e}")
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Only POST method is allowed"}, status=405)
