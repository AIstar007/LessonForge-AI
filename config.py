import os
from dotenv import load_dotenv

load_dotenv()

MAX_RETRIES = int(os.getenv("MAX_RETRIES", "2"))
