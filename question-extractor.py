from google import genai

from os import getenv
from dotenv import load_dotenv
load_dotenv()

client = genai.Client(api_key = getenv("API_KEY"))
