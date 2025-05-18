from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about-us/', views.about_us, name='about-us'),
    path('model-insight/', views.model_insight, name='model-insight'),
    path('motivation/', views.motivation, name='motivation'),
    path('team/', views.team, name='team'),
    path('feedback/', views.feedback, name='feedback'),
    path('feedback-submitted/', views.feedback_submitted,
         name='feedback-submitted'),
    path('api/analyze-tweet/', views.analyze_tweet, name='analyze-tweet'),
]
