# Disaster Tweet Analyzer

An ML-powered application that analyzes tweets to identify disaster-related information, location, sentiment, and disaster category.

## Project Overview

The Disaster Tweet Analyzer is a web application that uses machine learning to analyze tweets for disaster-related content. It can:

- Determine whether a tweet is about a real disaster
- Extract potential location mentions
- Categorize the type of disaster (earthquake, flood, wildfire, etc.)
- Analyze the sentiment of the tweet

## Features

- Real-time tweet analysis
- Disaster classification
- Location extraction
- Sentiment analysis
- Category identification

## Project Structure

```
disaster_app/
├── __init__.py         # Flask application factory
├── models/             # ML model files
├── static/             # Static assets (CSS, JS, images)
├── templates/          # HTML templates
├── utils/              # Utility functions for tweet analysis
└── views/              # Flask routes and view functions
```

## Installation

1. Clone the repository
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
3. Run the application:
   ```
   python run.py
   ```

## Dependencies

- Flask: Web framework
- NLTK: Natural Language Toolkit for sentiment analysis
- spaCy: For natural language processing and entity extraction
- scikit-learn: For machine learning models

## Usage

1. Access the application at `http://localhost:5000`
2. Enter a tweet in the input box
3. Click "Analyze" to see the analysis results

## License

See the LICENSE file for details.
