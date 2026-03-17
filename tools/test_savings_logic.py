
import requests
import json

def test_smart_routing_savings():
    url = "http://127.0.0.1:8045/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer sk-addaf3f6a20741dfb1a71d93f8ec5fac"
    }
    
    # We ask for an EXPENSIVE model (GPT-4)
    data = {
        "model": "gpt-4", 
        "messages": [{"role": "user", "content": "What is 1+1?"}]
    }

    print("Requesting EXPENSIVE model (gpt-4) for a SIMPLE task...")
    try:
        response = requests.post(url, headers=headers, json=data)
        result = response.json()
        
        # The 'model' field in the response will show what was ACTUALLY used
        actual_model = result.get('model', 'unknown')
        
        print("\n" + "="*50)
        print(f"REQUESTED MODEL: gpt-4")
        print(f"ACTUAL MODEL USED BY PROXY: {actual_model}") 
        print(f"RESPONSE: {result['choices'][0]['message']['content']}")
        print("="*50)
        
        if "gemini" in actual_model.lower():
            print("\n✅ PROOF OF SAVINGS: The proxy detected a simple task (or used your mapping) and routed to a CHEAPER Gemini model instead of GPT-4!")
        else:
            print("\nℹ️ Proxy used the requested model. Logic: Maps were followed.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_smart_routing_savings()
