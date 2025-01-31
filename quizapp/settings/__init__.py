import os

environment = os.getenv('DJANGO_ENV', 'local')
print(f"Using {environment} settings")

if environment == 'production':
    from .production import *
else:
    from .local import *
