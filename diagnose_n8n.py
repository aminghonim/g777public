import asyncio
import httpx
import sys

async def check_n8n():
    url = "http://localhost:5678/webhook/whatsapp"
    print(f"🔍 Checking N8N connection at: {url}")
    
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json={"test": "ping"}, timeout=5.0)
            print(f" N8N Reachable! Status: {resp.status_code}")
            print(f" Response: {resp.text}")
    except Exception as e:
        print(f" N8N Unreachable: {e}")

if __name__ == "__main__":
    if "httpx" not in sys.modules:
        # Just to confirm import worked generally
        pass
    asyncio.run(check_n8n())

