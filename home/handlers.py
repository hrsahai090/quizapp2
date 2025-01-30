from home.models import LogInfo
import logging
from django.apps import apps

class DatabaseLogHandler(logging.Handler):
    def emit(self, record):
        try:
            LogInfo = apps.get_model('home', 'LogInfo') 
            
            log_entry = LogInfo(
                message=self.format(record),
                level=record.levelname,
                view_name=record.name
            )
            log_entry.save()
        except Exception as e:
            print(f"Error saving log to database: {e}")