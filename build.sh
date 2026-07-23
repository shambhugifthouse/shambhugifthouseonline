#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate
python seed_shambhu_demo_data.py
python -c "import os, django; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shambhu_pos.settings'); django.setup(); from django.contrib.auth.models import User; from apps.authentication.models import UserProfile; user, _ = User.objects.get_or_create(username='admin'); user.set_password('admin123'); user.is_staff=True; user.is_superuser=True; user.save(); profile, _ = UserProfile.objects.get_or_create(user=user); profile.role='ADMIN'; profile.save()"

