
import asyncio
import os
import sys

# Ensure backend is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.ai_service import generate_ai_response

async def test_tokens():
    print("Testing AI Token Tracking...")
    prompt = "Hi, can you explain what a SaaS is in one sentence?"
    
    result = await generate_ai_response(prompt)
    
    print("\n" + "="*50)
    print(f"RESPONSE TEXT: {result.get('text')}")
    print(f"TOKENS FOUND: {result.get('usage')}")
    print("="*50)
    
    if result.get('usage') and result['usage'].get('total_tokens', 0) > 0:
        print("\nSUCCESS: Program is now reading tokens correctly!")
    else:
        print("\nFAILURE: Tokens are still 0. Check API response structure.")

if __name__ == "__main__":
    asyncio.run(test_tokens())
