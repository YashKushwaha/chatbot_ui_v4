import os
from fastapi.templating import Jinja2Templates

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

UPLOAD_DIR = os.path.join(PROJECT_ROOT, "uploads")
UI_BASE = os.path.join(PROJECT_ROOT, "front_end")

TEMPLATES_DIR = os.path.join(UI_BASE, "templates")
STATIC_DIR = os.path.join(UI_BASE, "static")
IMAGES_DIR = os.path.join(STATIC_DIR, "images")

templates = Jinja2Templates(directory=TEMPLATES_DIR)

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

IMAGES_FOLDER = os.path.join(PROJECT_ROOT, 'local_only', 'data', 'images')


