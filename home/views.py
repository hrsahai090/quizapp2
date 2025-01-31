from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from home.forms import LoginForm, RegisterForm, QuizForm
from django.contrib.auth import login, logout, authenticate
from .models import Quiz,QuizAttempt,Questions,QuizAnswer,Option
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta 
from django.http import JsonResponse
import logging 
from django.utils.timezone import now

logger = logging.getLogger(__name__)

def main_page(request):
    try:
        return render(request, 'home/mainpage.html')
    
    except Exception as e:
        logger.error(f"Error loading main page: {e}")
        messages.error(request, 'An error occurred while loading the page.')
        return redirect('main_page')


def log_in(request):
    
    try:           
        if request.method == 'GET':
            form = LoginForm()
            return render(request, 'home/login.html', {'form': form})
        elif request.method == 'POST':
            form = LoginForm(request.POST)
            if form.is_valid():
                username = form.cleaned_data['username']
                password = form.cleaned_data['password']
                user = authenticate(request,username=username,password=password)
                if user:
                    login(request, user)
                    messages.success(request,f'Hi {username.title()}, welcome back!')
                    logger.info(f"User {username} logged in successfully.")
                    return redirect('quiz_list')
                else:
                    messages.error(request,f'Invalid username or password')
                    logger.warning(f"Failed login attempt for username: {username}")
            return render(request,'home/login.html',{'form': form})
        
    except Exception as e:
        logger.error(f"Error during login: {e}")
        messages.error(request, 'An error occurred during login.')
        return redirect('log_in')
      

def register(request):
    
    try:
        if request.method == 'GET':
            form = RegisterForm()
            logger.info('GET request for registration form.')
            return render(request, 'home/register.html', {'form': form})
    
        if request.method == 'POST':
        
            form = RegisterForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                user.username = user.username.lower() 
                user.save()
                login(request, user)
                messages.success(request, 'You have successfully registered and logged in.')
                logger.info(f'Successful registration and login for user: {user.username}')
                return redirect('quiz_list')  
            else:
                messages.error(request, 'Registration failed. Please try again.')
                logger.warning(f'Registration failed for user: {request.POST}')
                return render(request, 'home/login.html', {'form': form})
            
    except Exception as e:
        logger.error(f"Error during registration: {e}")
        messages.error(request, 'An error occurred during registration.')
        return redirect('main_page')
        
def sign_out(request):
    try:
        logout(request)
        messages.success(request,f'You have been logged out.')
        logger.info(f"User {request.user.username} logged out.")
        return redirect('log_in')   
     
    except Exception as e:
        logger.error(f"Error during login: {e}")
        messages.error(request, 'An error occurred during logout.')
        return redirect('main_page')


@login_required
def quiz_list(request):
    
    try:
        quizzes = Quiz.objects.filter(is_deleted=False)
        return render(request, 'home/quiz_list.html', {'quizzes': quizzes})
    
    except Exception as e:
        logger.error(f"Error loading quiz list: {e}")
        messages.error(request, 'An error occurred while loading the quiz list.')
        return redirect('main_page')


@login_required
def quiz_take_up(request, id):
    try:
        quiz = get_object_or_404(Quiz, id=id, is_deleted=False)

        # Check if the quiz has no questions
        if not quiz.questions.exists():
            messages.warning(request, "This quiz has no questions. Please select another quiz.")
            return render(request, 'home/no_questions.html', {'quiz': quiz})  

        previous_attempts = QuizAttempt.objects.filter(user=request.user, quiz=quiz).count()
        if previous_attempts >= quiz.max_attempts:
            messages.error(request, "You have reached the maximum number of attempts for this quiz.")
            return render(request, 'home/quiz_limit_reached.html', {'quiz': quiz})

        quiz_attempt = QuizAttempt.objects.filter(user=request.user, quiz=quiz, status="IN_PROGRESS").first()

        if not quiz_attempt:
            quiz_attempt = QuizAttempt.objects.create(
                user=request.user,
                quiz=quiz,
                attempt_number=previous_attempts + 1,
                status="IN_PROGRESS",
                started_at=now(), 
            )

        if request.method == 'POST':
            score = 0
            for question in quiz.questions.all():
                user_answer = request.POST.get(f"question_{question.id}")

                if question.type == 'MCQ':
                    selected_option = Option.objects.get(id=user_answer)
                    QuizAnswer.objects.create(
                        session=quiz_attempt,
                        questions=question,
                        selected_option=selected_option
                    )
                    if selected_option.is_correct:
                        score += question.score
                else:
                    QuizAnswer.objects.create(
                        session=quiz_attempt,
                        questions=question,
                        typed_answer=user_answer
                    )
                    correct_answer = question.answer.strip().lower()
                    if correct_answer == user_answer.strip().lower():
                        score += question.score

            quiz_attempt.status = 'COMPLETED'
            quiz_attempt.completed_at = now()  
            quiz_attempt.score = score 
            quiz_attempt.save()

            messages.success(request, "Quiz submitted successfully!")
            return redirect('quiz_result', id=quiz.id)

        return render(request, 'home/quiz_take_up.html', {
            'quiz': quiz,
            'quiz_attempt': quiz_attempt,
        })

    except Exception as e:
        logger.error(f"Error starting quiz: {e}")
        messages.error(request, "An error occurred while starting the quiz. Please try again.")
        return redirect('quiz_list')


@login_required
def check_quiz_timer(request, id):
    try:
        quiz_attempt = QuizAttempt.objects.get(id=id, user=request.user)

        time_limit = quiz_attempt.started_at + quiz_attempt.quiz.duration

        if timezone.now() > time_limit:
            quiz_attempt.status = "COMPLETED"
            quiz_attempt.completed_at = timezone.now()  
            quiz_attempt.save()
            return JsonResponse({'status': 'expired', 'redirect_url': 'quiz/result/{}/'.format(quiz_attempt.quiz.id)})

        # Calculate the remaining time
        time_left = time_limit - timezone.now()
        time_left_seconds = time_left.total_seconds()

        minutes = int(time_left_seconds // 60)
        seconds = int(time_left_seconds % 60)

        return JsonResponse({
            'status': 'ongoing',
            'time_left': {'minutes': minutes, 'seconds': seconds}
        })

    except QuizAttempt.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Quiz attempt not found.'})


# @login_required
# def quiz_result(request, id):
#     try:
        
#         quiz = get_object_or_404(Quiz, id=id)

#         quiz_attempts = QuizAttempt.objects.filter(quiz=quiz, user=request.user, status='COMPLETED').order_by('-completed_at')
        
#         if quiz_attempts.exists():
#             quiz_attempt = quiz_attempts.first() 
#         else:
#             messages.error(request, "No completed attempts found for this quiz.")
#             return redirect('quiz_list')

#         quiz_answers = QuizAnswer.objects.filter(session=quiz_attempt)

#         score = 0
#         for answer in quiz_answers:
#             if answer.questions.type == 'MCQ':
#                 if answer.selected_option.is_correct:
#                     score += answer.questions.score
#             elif answer.questions.type == 'OPEN':
#                 correct_answer = answer.questions.answer.strip().lower()
#                 user_answer = answer.typed_answer.strip().lower()
#                 if correct_answer == user_answer:
#                     score += answer.questions.score

#         attempt_number = QuizAttempt.objects.filter(user=request.user, quiz=quiz).count()
#         max_attempts = quiz.max_attempts

#         if attempt_number > max_attempts:
#             messages.error(request, "You have reached the maximum number of attempts for this quiz.")
#             return render(request, 'home/quiz_result.html', {
#                 'quiz': quiz,
#                 'score': score,
#                 'attempt_number': attempt_number,
#                 'max_attempts_reached': True,
#             })

#         return render(request, 'home/quiz_result.html', {
#             'quiz': quiz,
#             'score': score,
#             'attempt_number': attempt_number,
#             'max_attempts_reached': False,
#         })
    
#     except Exception as e:
#         logger.error(f"Error in quiz_result view: {e}")
#         messages.error(request, "An error occurred while processing your result. Please try again.")
#         return redirect('quiz_list')
    
@login_required
def quiz_result(request, id):
    try:
        quiz = get_object_or_404(Quiz, id=id)

        quiz_attempts = QuizAttempt.objects.filter(quiz=quiz, user=request.user, status='COMPLETED').order_by('-completed_at')

        if not quiz_attempts.exists():
            messages.error(request, "No completed attempts found for this quiz.")
            return redirect('quiz_list')

        quiz_attempt = quiz_attempts.first() 
        score = quiz_attempt.score #retrive the score form quizattempt model

        attempt_number = QuizAttempt.objects.filter(user=request.user, quiz=quiz).count()
        max_attempts = quiz.max_attempts

        if attempt_number > max_attempts:
            messages.error(request, "You have reached the maximum number of attempts for this quiz.")
            return render(request, 'home/quiz_result.html', {
                'quiz': quiz,
                'score': score,
                'attempt_number': attempt_number,
                'max_attempts_reached': True,
            })

        return render(request, 'home/quiz_result.html', {
            'quiz': quiz,
            'score': score,
            'attempt_number': attempt_number,
            'max_attempts_reached': False,
        })

    except Exception as e:
        logger.error(f"Error in quiz_result view: {e}")
        messages.error(request, "An error occurred while processing your result. Please try again.")
        return redirect('quiz_list')


@login_required
def leaderboard(request, id):
    
    try:
        quiz = get_object_or_404(Quiz, id=id, is_deleted=False)

        leaderboard = QuizAttempt.objects.filter(quiz=quiz, status='COMPLETED').order_by('-score')

        leaderboard_data = []
        rank = 1
        for attempt in leaderboard:
            leaderboard_data.append({
                'rank': rank,
                'user': attempt.user,
                'score': attempt.score,
                'attempt_number': attempt.attempt_number
            })
            rank += 1

        return render(request, 'home/leaderboard.html', {'quiz': quiz, 'leaderboard': leaderboard_data})
    
    except Exception as e:
        logger.error(f"Error loading leaderboard: {e}")
        messages.error(request, 'An error occurred while loading the leaderboard.')
        return redirect('quiz_list')
    