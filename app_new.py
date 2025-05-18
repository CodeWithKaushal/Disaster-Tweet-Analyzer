from joblib import load
import logging
import json
import numpy as np
import subprocess
import re
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import pandas as pd
import spacy
import pickle
from flask import Flask, request, render_template, jsonify, redirect, url_for
import nltk

nltk.download("vader_lexicon")

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Ensure the spaCy model is downloaded
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

sia = SentimentIntensityAnalyzer()

# Load models
try:
    with open("vectorizer.pkl", "rb") as f:
        vectorizer = pickle.load(f)

    with open("lr_model.pkl", "rb") as f:
        model = pickle.load(f)

    # Try to load the more advanced model
    try:
        rf_model = load("rf_pipeline_model_bert_only.joblib")
        logger.info("Random Forest BERT model loaded successfully")
        use_advanced_model = True
    except Exception as e:
        logger.warning(f"Could not load advanced model: {e}")
        use_advanced_model = False

except Exception as e:
    logger.error(f"Error loading models: {e}")
    raise


def extract_locations(tweet):
    # spaCy entity recognition
    doc = nlp(tweet)
    locations = [
        ent.text for ent in doc.ents if ent.label_ == "GPE" or ent.label_ == "LOC"
    ]

    # Regular expression patterns for location extraction
    patterns = [
        r"\b\w+(?: city| town| village| state| province| country)\b",
        r"\b\w+(?: mountain| river| lake| ocean| sea)\b",
        r"\b[A-Z][a-z]+, [A-Z]{2}\b",  # US city, state format
    ]

    for pattern in patterns:
        regex_locations = re.findall(pattern, tweet)
        locations.extend(regex_locations)

    return list(set(locations))  # Remove duplicates


# Define disaster keywords
disaster_keywords = {
    # Natural Disasters
    "earthquake": [
        "earthquake",
        "quake",
        "tremor",
        "seismic",
        "aftershock",
        "quake swarm",
        "ground shaking",
        "temblor",
    ],
    "flood": [
        "flood",
        "flooding",
        "inundation",
        "deluge",
        "flash flood",
        "overflow",
        "torrential rain",
        "rainstorm",
    ],
    "hurricane": [
        "hurricane",
        "typhoon",
        "cyclone",
        "storm surge",
        "tropical storm",
        "severe storm",
    ],
    # Add more disaster types here...
}


def identify_disaster_type(tweet):
    tweet_lower = tweet.lower()

    # Check each disaster type and its keywords
    for disaster_type, keywords in disaster_keywords.items():
        for keyword in keywords:
            if keyword in tweet_lower:
                return disaster_type

    return None


def analyze_sentiment(tweet):
    sentiment_scores = sia.polarity_scores(tweet)
    compound_score = sentiment_scores["compound"]

    if compound_score >= 0.05:
        sentiment_label = "Positive"
    elif compound_score <= -0.05:
        sentiment_label = "Negative"
    else:
        sentiment_label = "Neutral"

    return {"label": sentiment_label, "score": abs(compound_score)}


@app.route("/")
def home():
    return render_template("index_new.html")


@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()
        tweet = data.get("tweet", "")

        if not tweet:
            return jsonify({"error": "No tweet provided"}), 400

        # Get prediction using the appropriate model
        if use_advanced_model:
            # Use the advanced model for prediction
            prediction = rf_model.predict([tweet])[0]
            probability = np.max(rf_model.predict_proba([tweet])[0])
        else:
            # Use the basic model for prediction
            tweet_vectorized = vectorizer.transform([tweet])
            prediction = model.predict(tweet_vectorized)[0]
            probability = np.max(model.predict_proba(tweet_vectorized)[0])

        is_disaster = bool(prediction)

        # Extract additional information
        locations = extract_locations(tweet)
        disaster_type = identify_disaster_type(tweet)
        sentiment = analyze_sentiment(tweet)

        response = {
            "tweet_text": tweet,
            "is_disaster": is_disaster,
            "confidence": float(probability),
            "locations": locations,
            "disaster_type": disaster_type,
            "sentiment": sentiment,
        }

        return jsonify(response)

    except Exception as e:
        logger.error(f"Error in prediction: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/about-us")
def about_us():
    return render_template("about-us_new.html")


@app.route("/team")
def team():
    return render_template("team.html")


@app.route("/motivation")
def motivation():
    return render_template("motivation.html")


@app.route("/model-insight")
def model_insight():
    return render_template("model-insight.html")


@app.route("/feedback")
def feedback():
    return render_template("feedback_new.html")


@app.route("/submitted_feedback", methods=["POST"])
def submitted_feedback():
    # Here you would typically save the feedback to a database
    name = request.form.get("name")
    email = request.form.get("email")
    feedback_text = request.form.get("feedback")
    rating = request.form.get("rating")

    # Log the feedback
    logger.info(
        f"Feedback received from {name} ({email}): Rating: {rating}, Text: {feedback_text}"
    )

    # In a real application, save this to a database

    return render_template("feedback_submitted.html")


@app.route("/api/v1/predict", methods=["POST"])
def api_predict():
    """API endpoint for prediction with proper error handling and documentation"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({"status": "error", "message": "No JSON data provided"}), 400

        tweet = data.get("tweet")

        if not tweet:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "No tweet text provided in the request",
                    }
                ),
                400,
            )

        # Get prediction using the appropriate model
        if use_advanced_model:
            prediction = rf_model.predict([tweet])[0]
            probability = np.max(rf_model.predict_proba([tweet])[0])
        else:
            tweet_vectorized = vectorizer.transform([tweet])
            prediction = model.predict(tweet_vectorized)[0]
            probability = np.max(model.predict_proba(tweet_vectorized)[0])

        is_disaster = bool(prediction)

        # Extract additional information
        locations = extract_locations(tweet)
        disaster_type = identify_disaster_type(tweet)
        sentiment = analyze_sentiment(tweet)

        response = {
            "status": "success",
            "prediction": {
                "text": tweet,
                "is_disaster": is_disaster,
                "confidence": float(probability),
                "locations": locations,
                "disaster_type": disaster_type,
                "sentiment": sentiment,
            },
        }

        return jsonify(response)

    except Exception as e:
        logger.error(f"API error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
