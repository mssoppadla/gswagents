# src/ui/dependencies.py
from pathlib import Path
from fastapi.templating import Jinja2Templates

# Calculate path relative to this file
base_path = Path(__file__).resolve().parent
templates_path = base_path / "templates"
templates = Jinja2Templates(directory=str(templates_path))

def get_templates():
    return templates
