import os
from dotenv import load_dotenv

# Load environment configuration (.env)
_env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
if os.path.exists(_env_path):
    load_dotenv(_env_path)

# Set defaults if not present
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "true")
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "qwiklabs-gcp-04-58a029e5210a")
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")
