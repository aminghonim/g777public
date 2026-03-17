"""
Health Check
============
Tries to import the webhook handler and db_service to ensure no syntax errors exist.
"""
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    print(" Importing DB Service...")
    from backend import db_service
    print(" DB Service Imported.")

    print(" Importing CRM Intelligence...")
    from backend import crm_intelligence
    print(" CRM Intelligence Imported.")

    print(" Importing Webhook Handler...")
    from backend import webhook_handler
    print(" Webhook Handler Imported.")
    
    print("\n🎉 All modules are healthy!")
except Exception as e:
    print(f"\n CRITICAL ERROR: {e}")
    import traceback
    traceback.print_exc()

