web: gunicorn shambhu_pos.wsgi:application --workers 2 --threads 4 --worker-class gthread --keep-alive 65 --max-requests 1000 --max-requests-jitter 50
