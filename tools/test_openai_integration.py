
from openai import OpenAI

# Initialize client pointing to local proxy
client = OpenAI(
    base_url="http://127.0.0.1:8045/v1",
    api_key="sk-addaf3f6a20741dfb1a71d93f8ec5fac"
)

try:
    print("Testing OpenAI Protocol via local Antigravity Proxy...")
    response = client.chat.completions.create(
        model="gemini-3-flash",
        messages=[{"role": "user", "content": "Hello! Explain local proxy benefits in 10 words."}]
    )

    print("\n" + "="*50)
    print(f"RESPONSE: {response.choices[0].message.content}")
    print(f"USAGE: {response.usage}")
    print("="*50)
    print("\nSUCCESS: Dashboard should now show this activity.")

except Exception as e:
    print(f"FAILED: {e}")
