from django.contrib import admin
from .models import Quiz,Option,Questions,User

class QuizAdmin(admin.ModelAdmin):
    pass

class OptionAdmin(admin.ModelAdmin):
    pass

class QuestionsAdmin(admin.ModelAdmin):
    pass

class UserAdmin(admin.ModelAdmin):
    pass

admin.site.register(Quiz, QuizAdmin)
admin.site.register(Questions,QuestionsAdmin) 
admin.site.register(Option,OptionAdmin) 
admin.site.register(User,UserAdmin) 