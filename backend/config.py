import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
