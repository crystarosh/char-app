import toml
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

def test_connection():
    print("--- Google Sheets Connection Test ---")
    
    # 1. Load Secrets
    secret_path = ".streamlit/secrets.toml"
    if not os.path.exists(secret_path):
        print(f"ERROR: {secret_path} not found.")
        return

    try:
        secrets = toml.load(secret_path)
        if "gcp_service_account" not in secrets:
            print("ERROR: [gcp_service_account] section missing in secrets.")
            return
            
        creds_dict = secrets["gcp_service_account"]
        
        # Key Fix
        if "\\n" in creds_dict["private_key"]:
            creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")

        print("Credentials loaded successfully.")
    except Exception as e:
        print(f"ERROR loading secrets: {e}")
        return

    # 2. Authorize
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        gc = gspread.authorize(creds)
        print("Authorization successful.")
    except Exception as e:
        print(f"ERROR in authorization: {e}")
        return

    # 3. List Spreadsheets (To see what is visible)
    print("\nListing available spreadsheets:")
    try:
        sheets = gc.openall()
        if not sheets:
            print("No spreadsheets found! (Did you share the sheet with the service account email?)")
        for sh in sheets:
            print(f"- Found: '{sh.title}' (ID: {sh.id})")
            
        print("\nAttempting to open 'CharDB'...")
        try:
            sh = gc.open("CharDB")
            print("SUCCESS! 'CharDB' opened.")
            print(f"Worksheet list: {[ws.title for ws in sh.worksheets()]}")
        except gspread.SpreadsheetNotFound:
            print("FAILURE: 'CharDB' not found in the list.")
            print("Please check: Did you invite the service account email as an Editor to the file itself?")
            print(f"Service Account Email: {creds_dict.get('client_email')}")
            
    except Exception as e:
        print(f"ERROR during listing/opening: {e}")

if __name__ == "__main__":
    test_connection()
