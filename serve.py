"""
Entry point for Render deployment.
Adds the correct paths and starts the backend.
"""
import sys
import os
from pathlib import Path

# Set up paths
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT / "finance_agents" / "src"))

# Set PYTHONPATH for subprocesses
os.environ["PYTHONPATH"] = f"{ROOT / 'backend'}:{ROOT / 'finance_agents' / 'src'}:{os.environ.get('PYTHONPATH', '')}"

# Import and run the app
from app.main import app  # noqa: F401, E402
