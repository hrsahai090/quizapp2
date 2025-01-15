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

@csrf_exempt

def main_page(request):
    return render(request, 'home/mainpage.html')

def log_in(request):           
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
                return redirect('quiz_list')
            else:
                messages.error(request,f'Invalid username or password')
        return render(request,'home/login.html',{'form': form})
    
def sign_out(request):
    logout(request)
    messages.success(request,f'You have been logged out.')
    return redirect('log_in')    

def register(request):
    if request.method == 'GET':
        form = RegisterForm()
        return render(request, 'home/register.html', {'form': form})
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower() 
            user.save()
            login(request, user)
            messages.success(request, 'You have successfully registered and logged in.')
            return redirect('quiz_list')  
        else:
            messages.error(request, 'Registration failed. Please try again.')
            return render(request, 'home/login.html', {'form': form})
        
        
@method_decorator(login_required, name='dispatch')
class QuizCreateView(CreateView):
    model = Quiz
    form_class = QuizForm
    template_name = ''
    success_url = reverse_lazy('quiz_list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user  
        messages.success(self.request, "Quiz created successfully!")
        return super().form_valid(form) 
    
@method_decorator(login_required, name='dispatch')
class QuizUpdateView(UpdateView):
    model = Quiz
    form_class = QuizForm
    template_name = ''
    context_object_name = 'quiz'

    def get_queryset(self):
        return Quiz.objects.filter(is_deleted=False)

    def form_valid(self, form):
        form.instance.updated_by = self.request.user 
        messages.success(self.request, "Quiz updated successfully!")
        return super().form_valid(form)
    
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
        quiz = self.get_object()
        quiz.is_deleted = True
        quiz.save()
        messages.success(self.request, "Quiz deleted successfully!")
        return redirect(self.success_url)
    
@login_required
def restore_quiz(request, id):
    quiz = get_object_or_404(Quiz, id=id, is_deleted=True)
    quiz.is_deleted = False
    quiz.save()
    messages.success(request, f"Quiz '{quiz.name}' has been restored.")
    return redirect('quiz_list')

@login_required
def quiz_list(request):
    quizzes = Quiz.objects.filter(is_deleted=False)
    return render(request, 'home/quiz_list.html', {'quizzes': quizzes})

#quiz details
@login_required
def quiz_detail(request, id):
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

@login_required
def leaderboard(request, id):
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
    