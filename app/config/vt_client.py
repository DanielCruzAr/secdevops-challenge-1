import vt
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("VT_API_KEY")

if not API_KEY:
    raise ValueError("VT_API_KEY not found in environment variables.")

client = vt.Client(API_KEY)
