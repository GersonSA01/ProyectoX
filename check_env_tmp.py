import os, socket
from pathlib import Path
print("CWD      :", Path.cwd())
env_path = Path.cwd() / ".env"
print(".env path:", env_path, "exists:", env_path.exists())

from dotenv import load_dotenv
load_dotenv(dotenv_path=env_path)
host = os.environ.get("SUPABASE_DB_HOST")
port = os.environ.get("SUPABASE_DB_PORT") or ""
name = os.environ.get("SUPABASE_DB_NAME")
user = os.environ.get("SUPABASE_DB_USER")
ssl  = os.environ.get("SUPABASE_DB_SSLMODE")
print("ENV HOST:", host)
print("ENV PORT:", port)
print("ENV NAME:", name)
print("ENV USER:", user)
print("ENV SSL :", ssl)

os.environ.setdefault("DJANGO_SETTINGS_MODULE","project.settings")
import django
django.setup()
from django.conf import settings
print("\nSETTINGS.DATABASES['default'] =")
print(settings.DATABASES['default'])
eff_host = settings.DATABASES['default'].get('HOST')
eff_port = settings.DATABASES['default'].get('PORT')

print("\nTesting DNS...")
try:
    gai = socket.getaddrinfo(eff_host, int(eff_port or 0))
    print("getaddrinfo OK ->", gai[0][4])
except Exception as e:
    print("DNS ERROR:", e)

print("\nTesting TCP connect (5s)...")
try:
    with socket.create_connection((eff_host, int(eff_port or 0)), timeout=5):
        print("TCP connect OK")
except Exception as e:
    print("TCP ERROR:", e)
