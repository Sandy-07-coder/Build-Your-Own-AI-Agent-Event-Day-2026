import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "development-secret"
)

ADMIN_USERNAME = os.getenv(
    "ADMIN_USERNAME",
    "admin"
)

ADMIN_PASSWORD = os.getenv(
    "ADMIN_PASSWORD",
    "admin123"
)

OPENAI_API_KEY = os.getenv(
    "OPENAI_API_KEY",
    ""
)

JUDGE_MODEL = os.getenv(
    "JUDGE_MODEL",
    "gpt-4o-mini"
)

REQUEST_TIMEOUT = int(
    os.getenv("REQUEST_TIMEOUT", "15")
)

EVENT_NAME = os.getenv(
    "EVENT_NAME",
    "BUILD YOUR OWN AI AGENT"
)
