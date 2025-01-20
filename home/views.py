from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from .forms import LoginForm
from .forms import LoginForm, RegisterForm
from django.contrib.auth import login, logout, authenticate
from django.utils.decorators import method_decorator
from .models import Quiz,QuizAttempt
from .forms import QuizForm
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.views.generic import UpdateView, DeleteView, CreateView
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import logging 

logger = logging.getLogger(__name__)

@csrf_exempt

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
        
        
@method_decorator(login_required, name='dispatch')
class QuizCreateView(CreateView):
    model = Quiz
    form_class = QuizForm
    template_name = ''
    success_url = reverse_lazy('quiz_list')
    
    def form_valid(self, form):
        
        try:
            form.instance.created_by = self.request.user  
            messages.success(self.request, "Quiz created successfully!")
            logger.info(f"Quiz created successfully by {self.request.user.username}.")
            return super().form_valid(form) 
        
        except Exception as e:
            logger.error(f"Error creating quiz: {e}")
            messages.error(self.request, 'An error occurred during quiz creation.')
            return redirect('quiz_list')
    
@method_decorator(login_required, name='dispatch')
class QuizUpdateView(UpdateView):
    model = Quiz
    form_class = QuizForm
    template_name = ''
    context_object_name = 'quiz'

    def get_queryset(self):
        return Quiz.objects.filter(is_deleted=False)

    def form_valid(self, form):
        
        try:
            form.instance.updated_by = self.request.user 
            messages.success(self.request, "Quiz updated successfully!")
            logger.info(f"Quiz updated successfully by {self.request.user.username}.")
            return super().form_valid(form)
        
        except Exception as e:
            logger.error(f"Error updating quiz: {e}")
            messages.error(self.request, 'An error occurred during updating quiz.')
            return redirect('quiz_list')
    
@method_decorator(login_required, name='dispatch')
class QuizDeleteView(DeleteView):
    model = Quiz
    template_name = ''
    context_object_name = 'quiz'
    success_url = reverse_lazy('quiz_list')  

    def get_queryset(self):
        #non-deleted quizzes
        return Quiz.objects.filter(is_deleted=False)

    def delete(self, request, *args, **kwargs):
        
        try:
            quiz = self.get_object()
            quiz.is_deleted = True
            quiz.save()
            messages.success(self.request, "Quiz deleted successfully!")
            logger.info(f"Quiz '{quiz.name}' deleted successfully by {self.request.user.username}.")
            return redirect(self.success_url)
        
        except Exception as e:
            logger.error(f"Error deleting quiz: {e}")
            messages.error(self.request, 'An error occurred during deleting a quiz.')
            return redirect('quiz_list')
    
@login_required
def restore_quiz(request, id):
    
    try:
        quiz = get_object_or_404(Quiz, id=id, is_deleted=True)
        quiz.is_deleted = False
        quiz.save()
        messages.success(request, f"Quiz '{quiz.name}' has been restored.")
        logger.info(f"Quiz '{quiz.name}' restored successfully by {request.user.username}.")
        return redirect('quiz_list')
    
    except Exception as e:
        logger.error(f"Error restoring quiz: {e}")
        messages.error(request, 'An error occurred while restoring the quiz.')
        return redirect('quiz_list')

@login_required
def quiz_list(request):
    
    try:
        quizzes = Quiz.objects.filter(is_deleted=False)
        return render(request, 'home/quiz_list.html', {'quizzes': quizzes})
    
    except Exception as e:
        logger.error(f"Error loading quiz list: {e}")
        messages.error(request, 'An error occurred while loading the quiz list.')
        return redirect('main_page')

#quiz details
@login_required
def quiz_detail(request, id):
    
    try:
        quiz = get_object_or_404(Quiz, id=id, is_deleted=False)
    
        quiz_attempts = QuizAttempt.objects.filter(user=request.user, quiz=quiz).count()
    
        if quiz_attempts >= quiz.max_attempts:
            messages.error(request,f"You have reached the maximum number of attempts ({quiz.max_attempts}) for this quiz.")
            return render(request, 'home/quiz_limit_reached.html',{'quiz': quiz})
    
        if quiz_attempts<quiz.max_attempts:  
            if request.method == 'POST':
                score = 0
                for question in quiz.questions.all():
                    user_answer = request.POST.get(f'question_{question.id}')
                    if user_answer:
                        if question.type == 'MCQ': 
                            is_correct = question.option_set.get(id=user_answer).is_correct
                            if is_correct:
                                score += question.score  
                
                        elif question.type == 'OPEN': 
                            if user_answer.strip().lower() == question.answer.strip().lower():
                                score += question.score 
                            
                attempt_number = quiz_attempts +1
                QuizAttempt.objects.create(
                    user=request.user,
                    quiz=quiz,
                    attempt_number=attempt_number,
                    score=score,
                    status='COMPLETED',
                    completed_at=timezone.now()
                )
            
                return render(request, 'home/quiz_result.html', {'score': score, 'attempt_number': attempt_number, 'quiz': quiz})
    
        return render(request, 'home/quiz_detail.html', {'quiz': quiz})
    
    except Exception as e:
        logger.error(f"Error viewing quiz details: {e}")
        messages.error(request, 'An error occurred while loading the quiz details.')
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
    