import os
from openai import OpenAI

# Option 1: set your key directly here (just for testing, remove after)
# os.environ["OPENAI_API_KEY"] = "sk-your-key-here"

# Option 2: load from .env file (recommended)
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("❌ No API key found. Check your .env file or environment variable.")
    exit(1)

print(f"Found key starting with: {api_key[:7]}...")

try:
    client = OpenAI(api_key=api_key)
    
    # Simple test call - a cheap embeddings request
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input="test connection"
    )
    print("✅ API key is working!")
    print(f"Embedding vector length: {len(response.data[0].embedding)}")

except Exception as e:
    print(f"❌ API key test failed: {e}")