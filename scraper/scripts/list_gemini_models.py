"""
List available Gemini models
"""

import os
from dotenv import load_dotenv
import pathlib

# Load environment variables
env_path = pathlib.Path(__file__).parent.parent.parent / '.env.local'
load_dotenv(env_path)

api_key = os.getenv('GEMINI_API_KEY')
print(f"API Key: {api_key[:20]}...")

try:
    import google.generativeai as genai

    genai.configure(api_key=api_key)

    print("\nAvailable models:")
    print("=" * 80)

    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            print(f"\nModel: {model.name}")
            print(f"Display Name: {model.display_name}")
            print(f"Description: {model.description}")
            print(f"Supported methods: {model.supported_generation_methods}")

except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
