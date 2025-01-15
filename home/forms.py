from django import forms
from .models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Quiz,Questions,Option

class LoginForm(forms.Form):
    username = forms.CharField(max_length=65)
    password = forms.CharField(max_length=65, widget=forms.PasswordInput)
    
class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username','email','password1','password2'] 
    
class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['name', 'description', 'duration', 'max_attempts','quiz_user']
        
class QuestionForm(forms.ModelForm):
    class Meta:
        model = Questions
        fields = ['question', 'type', 'answer', 'score'] 
        
class OptionForm(forms.ModelForm):
    class Meta:
        model = Option
        fields = ['option', 'is_correct']