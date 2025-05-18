# Disaster Tweet Analyzer

A machine learning-powered web application that analyzes tweets to detect disaster-related information. This project uses natural language processing and machine learning techniques to:

1. Predict if a tweet is about a real disaster
2. Extract potential locations mentioned
3. Identify the type of disaster being referenced
4. Analyze the sentiment of the tweet

## Features

- **Tweet Classification**: Predicts whether a tweet is about a real disaster or not with confidence score
- **Disaster Type Identification**: Categorizes tweets into specific disaster types (earthquake, flood, hurricane, etc.)
- **Location Extraction**: Uses Named Entity Recognition to identify potential locations mentioned in tweets
- **Sentiment Analysis**: Analyzes the emotional tone of tweets to provide additional context
- **Responsive Interface**: Works well on desktop and mobile devices
- **Available in Flask and Django**: Two versions of the application are provided

## Technical Stack

### Machine Learning & NLP

- Python
- scikit-learn
- NLTK (Natural Language Toolkit)
- spaCy for NER
- VADER Sentiment Analysis

### Web Development

- Flask version: Flask, HTML, CSS, JavaScript
- Django version: Django, HTML, CSS, JavaScript
- Bootstrap 5 for UI components
- Chart.js for data visualization

## Installation & Setup

### Prerequisites

- Python 3.8+
- pip package manager

### Installation Steps

1. Clone the repository:

```
git clone https://github.com/yourusername/Disaster-Tweet-Analyzer.git
cd Disaster-Tweet-Analyzer
```

2. Install dependencies:

```
pip install -r requirements.txt
```

3. Download required NLTK and spaCy data:

```
python -m nltk.downloader vader_lexicon
python -m spacy download en_core_web_sm
```

### Running the Flask Application

The Flask version is simpler to run and doesn't require database setup:

```
python app.py
```

Open your browser and go to: `http://localhost:5000`

### Running the Django Application

The Django version offers more features and a more modular structure:

1. Apply migrations:

```
python manage.py migrate
```

2. Run the server:

```
python run_django_server.bat   # On Windows
```

Or

```
python manage.py collectstatic --noinput
python manage.py runserver
```

Open your browser and go to: `http://localhost:8000`

## Project Structure

### Flask Version

- `app.py`: Main Flask application
- `templates/`: HTML templates for Flask
- `static/`: Static files (CSS, JS, images)

### Django Version

- `disaster_tweet_analyzer/`: Django project settings
- `tweet_analyzer/`: Django app with business logic
- `templates/`: HTML templates (both Flask and Django)
- `static/`: Static files
- `manage.py`: Django management script

## Model Information

Our disaster prediction model is trained on a dataset of over 10,000 tweets, with the following performance metrics:

- Accuracy: 96.2%
- Precision: 94.7%
- Recall: 92.8%
- F1 Score: 93.7%

We use a combination of Logistic Regression and Random Forest classifiers for the main prediction task.

## Contributors

- Team 3 - Infosys Springboard Project

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Thanks to Kaggle for providing the initial dataset
- Thanks to NLTK, spaCy, and scikit-learn communities for their excellent tools
