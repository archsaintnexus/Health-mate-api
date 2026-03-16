"""
Celery app initialization for Health Mate API.
This configures Celery to work with Django and execute async tasks.
"""
import os
from celery import Celery

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Initialize the Celery app
app = Celery('health_mate_api')

# Load configuration from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all registered Django apps
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    """Test task to verify Celery is working."""
    print(f"Request: {self.request!r}")
