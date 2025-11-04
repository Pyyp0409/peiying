# check_env.py
import sys
import os

print("=== VIRTUAL ENVIRONMENT CHECK ===")
print("Python executable:", sys.executable)
print("In virtual env:", 'grandstay_env' in sys.executable)
print("Current directory:", os.getcwd())

# Try imports
try:
    import plotly.express as px
    print("✅ Plotly imported from:", px.__file__)
except ImportError as e:
    print("❌ Plotly import failed:", e)