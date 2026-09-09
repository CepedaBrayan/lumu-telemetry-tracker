import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
RECEPTOR_PATH = PROJECT_ROOT / "telemetry-receptor"

sys.path.insert(0, str(RECEPTOR_PATH))
