import os

class Config:
    def __init__(self):
        self.celery_broker_url = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
        self.debug = os.environ.get('DEBUG', 'false').lower() == 'true'
        self.redis_host = os.environ.get('REDIS_HOST', 'localhost')
        self.redis_port = os.environ.get('REDIS_PORT', 6379)
