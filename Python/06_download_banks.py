import pandas as pd
import requests
from pathlib import Path

# ==========================================
# PROJECT PATHS
# ==========================================

RAW_FOLDER = Path("Data/Raw")

RAW_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)

print("Raw folder ready.")