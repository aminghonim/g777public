from ui.theme_manager import theme_manager

def verify_fix():
    try:
        colors = theme_manager.get_colors()
        print("Successfully called get_colors().")
        print(f"Sample tokens: mauve={colors.get('mauve')}, surface0={colors.get('surface0')}")
        
        required = ["mauve", "text", "surface0", "surface1", "subtext0"]
        missing = [t for t in required if t not in colors]
        
        if not missing:
            print("All required tokens found! Fix is verified.")
        else:
            print(f"Still missing tokens: {missing}")
            
    except Exception as e:
        print(f"Verification failed with error: {e}")

if __name__ == "__main__":
    verify_fix()
