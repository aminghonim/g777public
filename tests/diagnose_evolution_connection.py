#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Evolution API Connection Diagnostic Tool
يفحص الاتصال بين جميع مكونات النظام
"""

import requests
import json
import sys
import io
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ═══════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════
LOCAL_IP = "127.0.0.1"
EVOLUTION_PORT = 8080
N8N_PORT = 5678
BAILEYS_PORT = 3000

EVOLUTION_URL = f"http://{LOCAL_IP}:{EVOLUTION_PORT}"
N8N_URL = f"http://{LOCAL_IP}:{N8N_PORT}"
BAILEYS_URL = f"http://{LOCAL_IP}:{BAILEYS_PORT}"

INSTANCE_NAME = "SENDER"
API_KEY = "os.getenv('EVOLUTION_API_KEY', 'your_api_key_here')"

# ═══════════════════════════════════════════════════════════
# Helper Functions
# ═══════════════════════════════════════════════════════════

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def print_step(num, text):
    print(f"\n[{num}] {text}")

def check_service(name, url, timeout=5):
    """فحص حالة الخدمة"""
    try:
        resp = requests.get(url, timeout=timeout)
        if resp.status_code == 200:
            print(f"   {name} is UP (Status: {resp.status_code})")
            return True, resp
        else:
            print(f"    {name} returned status: {resp.status_code}")
            return False, resp
    except requests.exceptions.ConnectionError:
        print(f"   {name} is DOWN (Connection Refused)")
        return False, None
    except requests.exceptions.Timeout:
        print(f"  ⏱️  {name} Timeout")
        return False, None
    except Exception as e:
        print(f"   {name} Error: {str(e)}")
        return False, None

def check_evolution_instance():
    """فحص حالة Instance في Evolution API"""
    try:
        url = f"{EVOLUTION_URL}/instance/connectionState/{INSTANCE_NAME}"
        headers = {"apikey": API_KEY}
        resp = requests.get(url, headers=headers, timeout=10)
        
        if resp.status_code == 200:
            data = resp.json()
            state = data.get('instance', {}).get('state', 'unknown')
            print(f"   Instance '{INSTANCE_NAME}' State: {state}")
            
            if state == 'open':
                print(f"   WhatsApp is CONNECTED!")
                return True
            else:
                print(f"   WhatsApp is NOT connected (State: {state})")
                return False
        else:
            print(f"   Failed to get instance state (Status: {resp.status_code})")
            print(f"     Response: {resp.text[:200]}")
            return False
    except Exception as e:
        print(f"   Error checking instance: {str(e)}")
        return False

def check_evolution_webhook():
    """فحص إعدادات Webhook في Evolution API"""
    try:
        url = f"{EVOLUTION_URL}/webhook/find/{INSTANCE_NAME}"
        headers = {"apikey": API_KEY}
        resp = requests.get(url, headers=headers, timeout=10)
        
        if resp.status_code == 200:
            data = resp.json()
            webhook_url = data.get('webhook', {}).get('url', 'Not Set')
            enabled = data.get('webhook', {}).get('enabled', False)
            events = data.get('webhook', {}).get('events', [])
            
            print(f"   Webhook Configuration:")
            print(f"     URL: {webhook_url}")
            print(f"     Enabled: {enabled}")
            print(f"     Events: {', '.join(events)}")
            
            # Check if webhook points to n8n
            if 'localhost:5678' in webhook_url or f'{LOCAL_IP}:5678' in webhook_url:
                print(f"   Webhook correctly points to n8n")
                return True
            else:
                print(f"    Webhook does NOT point to n8n!")
                print(f"     Expected: http://localhost:5678/webhook/whatsapp")
                print(f"     Or: http://{LOCAL_IP}:5678/webhook/whatsapp")
                return False
        else:
            print(f"   Failed to get webhook config (Status: {resp.status_code})")
            return False
    except Exception as e:
        print(f"   Error checking webhook: {str(e)}")
        return False

def check_n8n_webhook():
    """فحص إذا n8n جاهز لاستقبال الـ webhook"""
    try:
        # Try to access n8n healthz endpoint
        url = f"{N8N_URL}/healthz"
        resp = requests.get(url, timeout=5)
        
        if resp.status_code == 200:
            print(f"   n8n is healthy and ready")
            return True
        else:
            print(f"    n8n returned status: {resp.status_code}")
            return False
    except Exception as e:
        print(f"   Cannot reach n8n: {str(e)}")
        return False

# ═══════════════════════════════════════════════════════════
# Main Diagnostic Flow
# ═══════════════════════════════════════════════════════════

def main():
    print_header("🔍 G777 Evolution API Connection Diagnostic")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Local IP: {LOCAL_IP}")
    
    results = {
        "evolution_api": False,
        "evolution_instance": False,
        "evolution_webhook": False,
        "n8n": False,
        "baileys": False
    }
    
    # Step 1: Check Evolution API
    print_step(1, "Checking Evolution API Service")
    results["evolution_api"], _ = check_service(
        "Evolution API", 
        f"{EVOLUTION_URL}/manager/instances"
    )
    
    # Step 2: Check Evolution Instance
    if results["evolution_api"]:
        print_step(2, f"Checking Instance '{INSTANCE_NAME}'")
        results["evolution_instance"] = check_evolution_instance()
    else:
        print_step(2, "⏭️  Skipping instance check (Evolution API is down)")
    
    # Step 3: Check Evolution Webhook Configuration
    if results["evolution_api"]:
        print_step(3, "Checking Webhook Configuration")
        results["evolution_webhook"] = check_evolution_webhook()
    else:
        print_step(3, "⏭️  Skipping webhook check (Evolution API is down)")
    
    # Step 4: Check n8n
    print_step(4, "Checking n8n Service")
    results["n8n"] = check_n8n_webhook()
    
    # Step 5: Check Baileys Service (Legacy)
    print_step(5, "Checking Baileys Service (Legacy)")
    baileys_up, _ = check_service("Baileys Service", f"{BAILEYS_URL}/health")
    results["baileys"] = baileys_up
    
    if baileys_up:
        print(f"    WARNING: Baileys Service is running!")
        print(f"     This might conflict with Evolution API")
        print(f"     Consider stopping Baileys if using Evolution API")
    
    # ═══════════════════════════════════════════════════════════
    # Final Report
    # ═══════════════════════════════════════════════════════════
    print_header(" Diagnostic Summary")
    
    all_good = (
        results["evolution_api"] and 
        results["evolution_instance"] and 
        results["evolution_webhook"] and 
        results["n8n"]
    )
    
    if all_good:
        print("\n🎉 ALL SYSTEMS OPERATIONAL!")
        print("\nYour WhatsApp bot should be working correctly.")
        print("If you're still having issues, check n8n workflow executions.")
    else:
        print("\n  ISSUES DETECTED!")
        print("\n🔧 Recommended Actions:")
        
        if not results["evolution_api"]:
            print("  1. Start Evolution API container:")
            print("     docker ps -a | grep evolution")
            print("     docker start evolution-api")
        
        if not results["evolution_instance"]:
            print("  2. Check WhatsApp connection:")
            print(f"     Visit: http://{LOCAL_IP}:{EVOLUTION_PORT}/instance/connect/{INSTANCE_NAME}")
            print("     Scan QR code if needed")
        
        if not results["evolution_webhook"]:
            print("  3. Configure webhook to point to n8n:")
            print(f"     URL: http://localhost:5678/webhook/whatsapp")
            print(f"     See: CONNECT_EVOLUTION_WEBHOOK.md")
        
        if not results["n8n"]:
            print("  4. Start n8n container:")
            print("     docker start n8n-automation")
        
        if results["baileys"]:
            print("  5. Consider stopping Baileys Service:")
            print(f"     docker stop baileys-service")
    
    print("\n" + "="*60)
    
    # Return exit code
    sys.exit(0 if all_good else 1)

if __name__ == "__main__":
    main()

