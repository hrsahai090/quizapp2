import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    id = models.UUIDField(primary_key=True,default= uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, null=False)
    is_admin = models.BooleanField(default=False)
    image = models.ImageField(upload_to='user_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default = False)
    fullname = models.CharField(max_length=256)
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',  
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions_set',  
        blank=True
    )
    def __str__(self):
        return self.username
    
class Quiz(models.Model):
    id = models.UUIDField(primary_key=True,default= uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    duration = models.DurationField(help_text="in minutes")
    max_attempts = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default = False)
    quiz_user = models.ManyToManyField(User, related_name='quizusers',blank=True)
    
    def __str__(self):
        return self.name
    
class Questions(models.Model):
    QUESTION_TYPES=[
        ('MCQ', 'Multiple Choice Question'),
        ('OPEN','Open Ended'),
    ]
    id = models.UUIDField(primary_key=True, default= uuid.uuid4, editable=False)
    question = models.TextField()
    type = models.CharField(max_length=10, choices = QUESTION_TYPES, default = 'MCQ')
    answer = models.TextField(blank = True, null=True) #open Ended
    score = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default = False)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    
    def __str__(self):
        return self.question

class Option(models.Model):
    
    id = models.UUIDField(primary_key=True,default= uuid.uuid4, editable=False)
    option = models.CharField(max_length=100)
    is_correct = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default = False)
    question = models.ForeignKey(Questions, on_delete=models.CASCADE, )
    
    def __str__(self):
         return f"{self.option}"
        
class QuizAttempt(models.Model):
    STATUS_CHOICES = (
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
    )
    id = models.UUIDField(primary_key=True,default= uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_user')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='quiz_question')
    attempt_number = models.PositiveIntegerField()
    score = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='IN_PROGRESS')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default = False)

    def __str__(self):
        return f"Attempt {self.attempt_number} by {self.user} for {self.quiz}"

    
