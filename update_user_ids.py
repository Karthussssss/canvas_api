from utils.credential_manager import CredentialManager

def main():
    """Update missing user IDs for all students"""
    print("Starting to update missing user IDs...")
    
    manager = CredentialManager()
    manager.update_missing_user_ids()
    
    print("Finished updating user IDs.")

if __name__ == "__main__":
    main() 