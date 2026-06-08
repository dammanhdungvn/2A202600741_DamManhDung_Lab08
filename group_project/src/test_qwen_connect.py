import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

QWEN_API_KEY = os.getenv("QWEN_API_KEY")
QWEN_BASE_URL = os.getenv(
    "QWEN_BASE_URL", "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
)
QWEN_MODEL_NAME = os.getenv("QWEN_MODEL_NAME")

if not QWEN_API_KEY:
    raise ValueError("Missing QWEN_API_KEY in .env")

if not QWEN_MODEL_NAME:
    raise ValueError("Missing QWEN_MODEL in .env")

client = OpenAI(
    api_key=QWEN_API_KEY,
    base_url=QWEN_BASE_URL,
)

response = client.chat.completions.create(
    model=QWEN_MODEL_NAME,
    messages=[{"role": "user", "content": "Reply only: Qwen connection successful"}],
)

print(response.choices[0].message.content)
