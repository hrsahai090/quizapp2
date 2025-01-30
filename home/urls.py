from django.urls import path
from . import views

urlpatterns = [
    path('', views.main_page, name='main_page'),
    path('login/', views.log_in, name='log_in'),
    path('signout/', views.sign_out, name='sign_out'),
    path('register/', views.register, name='register'),
    path('quiz_list/', views.quiz_list, name='quiz_list'),
    path('quiz/take_up/<uuid:id>/', views.quiz_take_up, name='quiz_take_up'),
    path('check_timer/<uuid:id>/', views.check_quiz_timer, name='check_timer'), 
    path('quiz/result/<uuid:id>/', views.quiz_result, name='quiz_result'),
    path('quiz/leaderboard/<uuid:id>/', views.leaderboard, name='leaderboard'),
]
