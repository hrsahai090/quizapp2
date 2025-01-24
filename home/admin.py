from django.contrib import admin
from .models import Quiz,Option,Questions,User,LogInfo

class LogInfoAdmin(admin.ModelAdmin):
    list_display = ('level', 'message', 'created_at', 'view_name')
    search_fields = ('level', 'message', 'view_name')
    list_filter = ('level')
    ordering = ('-created_at') 
    
admin.site.register(Quiz)
admin.site.register(Questions) 
admin.site.register(Option) 
admin.site.register(User) 
admin.site.register(LogInfo,LogInfoAdmin)