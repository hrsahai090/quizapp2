from django.contrib import admin
from .models import Quiz,Option,Questions,User,LogInfo

class LogInfoAdmin(admin.ModelAdmin):
    list_display = ('level', 'message', 'created_at', 'view_name')
    search_fields = ('level', 'message', 'view_name')
    list_filter = ['level']
    ordering = ['-created_at'] 
    
admin.site.register(LogInfo,LogInfoAdmin)

admin.site.register(Quiz)
admin.site.register(Questions) 
class OptionAdmin(admin.ModelAdmin):
    list_display = ('option', 'question', 'is_correct', 'created_at', 'updated_at')
    search_fields = ('option',)
    list_filter = ('is_correct',)

#filter mcq type questions
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "question":
            kwargs["queryset"] = Questions.objects.filter(type='MCQ')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(Option, OptionAdmin)

admin.site.register(User)