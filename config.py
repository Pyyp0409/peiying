# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "your_supabase_project_url_here")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "your_supabase_anon_key_here")

# Application Settings
APP_TITLE = "Grand Stay Hotel Management System"
APP_VERSION = "1.0.0"
AUTO_CANCEL_MINUTES = 15

# Color Scheme
COLOR_SCHEME = {
    "primary": "#3498DB",
    "secondary": "#2C3E50", 
    "success": "#27AE60",
    "warning": "#F39C12",
    "danger": "#E74C3C",
    "info": "#17A2B8"
}