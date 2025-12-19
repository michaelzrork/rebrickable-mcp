import logging
import os
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', stream=sys.stderr)

# Check if environment variables are already set (e.g., by Railway)
REBRICKABLE_API_KEY = os.getenv("REBRICKABLE_API_KEY")
REBRICKABLE_USER_TOKEN = os.getenv("REBRICKABLE_USER_TOKEN")
BASE_URL = "https://rebrickable.com/api/v3"

logging.info(f"REBRICKABLE_API_KEY set: {REBRICKABLE_API_KEY is not None}")
logging.info(f"REBRICKABLE_USER_TOKEN set: {REBRICKABLE_USER_TOKEN is not None}")