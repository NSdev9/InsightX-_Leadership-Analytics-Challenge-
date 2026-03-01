import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("🚨 OPENAI_API_KEY not found in .env")

client = OpenAI(api_key=api_key)


def call_openai(prompt, temperature=0.2):
    """
    Accepts plain text prompt.
    Internally converts to proper messages format.
    """

    try:
        print("🔑 Using configured API key...")

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful data analyst."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature
        )

        print("✅ API call successful")

        return response

    except Exception as e:
        print("❌ OpenAI API Error:")
        print(str(e))
        return None