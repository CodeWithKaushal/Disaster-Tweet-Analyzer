from flask import Flask, request, render_template, jsonify
import torch
import pandas as pd
from transformers import AutoTokenizer, AutoModel
from joblib import load

app = Flask(__name__)

# Load the Random Forest model pipeline
rf_pipeline_loaded = load('rf_pipeline_model_bert_only.joblib')

# Load the BERT tokenizer and model
tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')
bert_model = AutoModel.from_pretrained('bert-base-uncased')

# Function to get BERT embedding for a sentence
def get_bert_embedding(sentence):
    
    inputs = tokenizer(sentence, return_tensors="pt", truncation=True, padding="max_length", max_length=128)
    with torch.no_grad():
        outputs = bert_model(**inputs)
        embedding = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
    return embedding

# Function to predict disaster-related information from a tweet
def predict_disaster_tweet(tweet_text):
    bert_embedding = get_bert_embedding(tweet_text)
    bert_embedding_df = pd.DataFrame([bert_embedding], columns=[f'bert_{i}' for i in range(768)])
    prediction = rf_pipeline_loaded.predict(bert_embedding_df)[0]
    is_disaster = "Disaster" if prediction == 1 else "Not Disaster"

    # Dummy placeholders for category, location, and sentiment, replace with actual logic if available
    category = "Hurricane" if is_disaster == "Disaster" else "None"
    location = "Florida" if is_disaster == "Disaster" else "Unknown"
    sentiment = "Negative" if is_disaster == "Disaster" else "Neutral"

    return is_disaster, location, category, sentiment

# Route to render the main page
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

# Prediction API endpoint
@app.route("/predict", methods=["POST"])
def predict():
    data = request.json
    tweet_text = data.get("tweet", "")

    # Predict disaster-related information
    is_disaster, location, category, sentiment = predict_disaster_tweet(tweet_text)

    # Create response data
    response_data = {
        "tweet_text": tweet_text,
        "is_disaster": is_disaster,
        "location": location,
        "category": category,
        "sentiment": sentiment
    }

    return jsonify(response_data)
@app.route('/feedback')
def feedback():
    return render_template('feedback.html')
@app.route('/submitted_feedback', methods=['POST'])
def feedback_submited():
    return render_template('feedback_submited.html')
@app.route('/motivation')
def motivation():
    return render_template('motivation.html')
@app.route('/model-insight')
def model_insight():
    return render_template('model-insight.html')
@app.route('/about-us')
def about_us():
    return render_template('about-us.html')
if __name__ == "__main__":
    app.run(debug=True)
