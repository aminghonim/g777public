
from duckduckgo_search import DDGS
import json

print("Testing DuckDuckGo Search...")
ddgs = DDGS()

query = 'site:facebook.com "chat.whatsapp.com" ملابس'
print(f"Query: {query}")

try:
    results = ddgs.text(query, max_results=5)
    print(f"Raw Results Type: {type(results)}")
    
    # DDGS might return a generator or list
    results_list = list(results)
    
    print(f"Count: {len(results_list)}")
    if results_list:
        print("First Result Structure:")
        print(json.dumps(results_list[0], indent=2, ensure_ascii=False))
    else:
        print("No results returned from DDGS.")

except Exception as e:
    print(f"Error: {e}")
