import os
import sys
import traceback

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def check_imports():
    print("Checking imports for all UI modules...")
    
    modules_to_check = [
        'ui.layout',
        'ui.pairing_page',
        'ui.crm_page',
        'ui.products_page',
        'ui.business_setup_page',
        'ui.opportunity_hunter_page',
        'ui.theme_settings_page',
        'ui.modules.group_sender',
        'ui.modules.members_grabber',
        'ui.modules.links_grabber',
        'ui.modules.number_filter',
        'ui.modules.account_warmer',
        'ui.modules.automation_hub',
        'ui.modules.maps_extractor',
        'ui.modules.social_extractor',
        'ui.modules.poll_sender',
        'ui.modules.cloud_hub',
        'ui.translations'
    ]
    
    failed = []
    
    for module in modules_to_check:
        try:
            print(f"Importing {module}...", end="", flush=True)
            __import__(module)
            print(" OK")
        except Exception:
            print(" FAILED")
            print(f"Error importing {module}:")
            traceback.print_exc()
            failed.append(module)
            print("-" * 40)
            
    if failed:
        print(f"\nFound {len(failed)} broken modules: {', '.join(failed)}")
        sys.exit(1)
    else:
        print("\nAll modules imported successfully.")
        sys.exit(0)

if __name__ == "__main__":
    check_imports()
