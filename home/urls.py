from django.urls import path
from . import views
from .views import QuizCreateView, QuizUpdateView, QuizDeleteView, restore_quiz

urlpatterns = [
    path('', views.main_page, name='main_page'),
    path('Login/', views.log_in, name='log_in'),
    path('Signout/', views.sign_out, name='sign_out'),
    path('register/', views.register, name='register'),
    path('quizzes/', views.quiz_list, name='quiz_list'),
    path('quiz/<uuid:id>/', views.quiz_detail, name='quiz_detail'),
    path('quizzes/create/', QuizCreateView.as_view(), name='quiz_create'),
    path('quizzes/<uuid:pk>/edit/', QuizUpdateView.as_view(), name='quiz_edit'),
    path('quizzes/<uuid:pk>/delete/', QuizDeleteView.as_view(), name='quiz_delete'),
    path('quizzes/<uuid:id>/restore/', restore_quiz, name='quiz_restore'),
    path('quiz/<uuid:id>/leaderboard/', views.leaderboard, name='leaderboard'),
    
]