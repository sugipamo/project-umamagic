import os
import sys
from pathlib import Path
import subprocess
import inspect

COMMANDS = {
    "up": "docker compose up -d --build",
    "down": "docker compose down",
    "restart": "docker compose restart",
    "logs": "docker compose logs",
    "exec": "docker compose exec",
    "gitfetch": "git fetch -p",
    "migrate": "docker compose exec django bash -c 'python manage.py makemigrations && python manage.py migrate'",
    "migrate_reset": "docker compose exec django bash -c 'python manage.py migrate --fake && python manage.py migrate'",
    "start": "docker compose exec django bash -c 'gunicorn --workers 4 --threads 2 umamagic.wsgi:application --bind'",
    "test_start": "docker compose exec django python manage.py runserver 0.0.0.0:8000",
    "test": "docker compose exec django bash -c 'python manage.py test'",
    "pytest": "docker compose exec django bash -c 'pytest -v -n auto'",    
}


args = sys.argv[1:]
if not args:
    args = input("Enter command: ").split()

if not args:
    print("No command entered")
    sys.exit()

os.chdir(Path(__file__).parent)


subprocess.run(COMMANDS[args[0]].format(*args[1:]), shell=True)