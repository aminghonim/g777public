from backend.db_service import get_db_cursor

def cleanup():
    print("🧹 Cleaning up bad training samples...")
    with get_db_cursor() as cur:
        # Delete samples that explicitly start with unwanted phrases or contain meta-commentary keywords
        cur.execute("""
            DELETE FROM bot_training_samples 
            WHERE humanized_response LIKE 'تمام يا فندم%' 
            OR humanized_response LIKE 'بصفتي%'
            OR humanized_response LIKE 'أهلاً بك%'
        """)
        print(f" Deleted {cur.rowcount} low-quality samples.")

if __name__ == "__main__":
    cleanup()

