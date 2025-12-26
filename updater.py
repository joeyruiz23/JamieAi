import requests
import os

GITHUB_RAW_URL = "https://raw.githubusercontent.com/joeyruiz23/JamieAi/main/jamie.py"

def download_latest():
    try:
        r = requests.get(GITHUB_RAW_URL)
        if r.status_code == 200:
            with open("jamie.py", "w", encoding="utf-8") as f:
                f.write(r.text)
            return "Update complete. Restart Jamie."
        else:
            return f"Download failed – GitHub status {r.status_code}"
    except Exception as e:
        return f"Error: {e}"
