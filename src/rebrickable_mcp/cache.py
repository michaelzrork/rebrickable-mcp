# cache.py
import csv
import zipfile
import httpx
from io import BytesIO
from pathlib import Path

CACHE_DIR = Path("./cache")
REBRICKABLE_CDN = "https://cdn.rebrickable.com/media/downloads"

# In-memory storage
COLORS = {} # {id: {"name": "Black", "rgb": "05131D", "is_trans": "f"}}

def download_colors():
    """Downlaod colors.csv.zip, extract, save locally, store last-modified timestamp."""
    CACHE_DIR.mkdir(exist_ok=True)
    
    url = f"{REBRICKABLE_CDN}/colors.csv.zip"
    
    with httpx.Client() as client:
        response = client.get(url)
        response.raise_for_status()
        last_modified = response.headers.get("last-modified", "")
        
        # Extract CSV from zip
        with zipfile.ZipFile(BytesIO(response.content)) as zf:
            with zf.open("colors.csv") as f:
                content = f.read().decode("utf-8")
                
        # Save CSV locally
        (CACHE_DIR / "colors.csv").write_text(content)
        
        # Save last-modified timestamp
        (CACHE_DIR / "colors_last_modified.txt").write_text(last_modified)
        
    return last_modified

def load_colors():
    """Load colors from cached CSV into memory."""
    global COLORS
    
    cache_file = CACHE_DIR / "colors.csv"
    
    if not cache_file.exists():
        download_colors()
    
    with open(cache_file) as f:
        reader = csv.DictReader(f)
        COLORS.clear()
        COLORS.update({
            int(row["id"]): {"name": row["name"], "rgb": row["rgb"], "is_trans": row["is_trans"]}
            for row in reader
        })

    return len(COLORS)