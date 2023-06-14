from django.urls import path
from . import views
from .views import *
from django.views.generic import TemplateView

# app_nam = 'vocab'

urlpatterns = [
    path('', views.main, name='main'),
    path('search/', SearchResultsView.as_view(), name='search_results'),
    path('login/', LoginUser.as_view(), name='login'),
    path('logout/', logout_user, name='logout'),
    path('register/',  RegisterUser.as_view(), name='register'),
    path('glossary/', views.terms_list, name='terms_list'),

    # изучение слов
    path('learning/', views.learn, name='learn'),
    path('learning/check_quiz_word', views.check_quiz_word, name='check_words'),
    path('learning/quiz', views.quiz, name='quiz'),
    path('learning/quiz_result', views.quiz_result, name='quiz_result'),
    path('learning/all_words_learned', views.all_words_learned, name='all_words_learned'),

    # повторение
    path('repetition/', views.repeat, name='repeat'),
    path('repetition/repeat', views.repeat_words, name='repeat_words'),
    path('repetition/repeat_result', views.repeat_result, name='repeat_result'),
    path('repetition/no_words_learned', views.no_words_learned, name='no_words_learned'),
]


