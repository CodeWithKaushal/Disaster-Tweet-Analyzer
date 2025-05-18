from flask import Blueprint, render_template, request, jsonify
from disaster_app.utils.tweet_analyzer import predict_tweet

# Create blueprint
bp = Blueprint('main', __name__)

# Route to render the main page


@bp.route("/", methods=["GET"])
def index():
    return render_template("index.html")

# Prediction API endpoint


@bp.route("/predict", methods=["POST"])
def predict():
    data = request.json
    tweet_text = data.get("tweet", "")

    # Predict disaster-related information
    prediction_result = predict_tweet(tweet_text)

    # Create response data
    response_data = {
        "tweet_text": tweet_text,
        "is_disaster": prediction_result["is_disaster"],
        "location": prediction_result["location"],
        "category": prediction_result["category"],
        "sentiment": prediction_result["sentiment"]
    }

    return jsonify(response_data)

# Additional routes


@bp.route('/feedback')
def feedback():
    return render_template('feedback.html')


@bp.route('/submitted_feedback', methods=['POST'])
def feedback_submitted():
    return render_template('feedback_submitted.html')


@bp.route('/motivation')
def motivation():
    return render_template('motivation.html')


@bp.route('/model-insight')
def model_insight():
    return render_template('model-insight.html')


@bp.route('/about-us')
def about_us():
    return render_template('about-us.html')


@bp.route('/team')
def team():
    return render_template('team.html')
