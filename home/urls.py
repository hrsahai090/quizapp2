from django.urls import path
from . import views
from .views import QuizCreateView, QuizUpdateView, QuizDeleteView, restore_quiz

urlpatterns = [
    path('', views.main_page, name='main_page'),
    path('login/', views.log_in, name='log_in'),
    path('signout/', views.sign_out, name='sign_out'),
    path('register/', views.register, name='register'),
    path('quiz_list/', views.quiz_list, name='quiz_list'),
    path('quiz/<uuid:pk>/', views.quiz_detail, name='quiz_detail'),
    # path('quiz_list/create/', QuizCreateView.as_view(), name='quiz_create'),
    # path('quiz_list/<uuid:pk>/edit/', QuizUpdateView.as_view(), name='quiz_edit'),
    # path('quiz_list/<uuid:pk>/delete/', QuizDeleteView.as_view(), name='quiz_delete'),
    # path('quiz_list/<uuid:pk>/restore/', restore_quiz, name='quiz_restore'),
    path('quiz/<uuid:pk>/detail/', views.quiz_detail, name='quiz_detail'),
    path('quiz/<uuid:attempt_id>/remaining_time/', views.remaining_time, name='remaining_time'),
    path('quiz/<uuid:pk>/time_up/', views.quiz_time_up, name='quiz_time_up'),
    path('quiz/<uuid:pk>/leaderboard/', views.leaderboard, name='leaderboard'),
    
]