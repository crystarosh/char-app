import toml
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json

def migrate_data():
    print("--- Data Migration: Local JSON -> Google Sheet ---")
    
    # 1. Load Local JSON
    json_path = os.path.join("data", "characters.json")
    if not os.path.exists(json_path):
        print("Error: data/characters.json not found.")
        return
        
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            local_data = json.load(f)
        print(f"Loaded {len(local_data)} characters from local JSON.")
        if not local_data:
            print("No data to migrate. Exiting.")
            return
    except Exception as e:
        print(f"Error loading local JSON: {e}")
        return

    # 2. Connect to Sheet
    secret_path = ".streamlit/secrets.toml"
    try:
        secrets = toml.load(secret_path)
        creds_dict = secrets["gcp_service_account"]
        if "\\n" in creds_dict["private_key"]:
            creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
            
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        gc = gspread.authorize(creds)
        sh = gc.open("CharDB")
        ws = sh.sheet1
        print("Connected to Google Sheet 'CharDB'.")
    except Exception as e:
        print(f"Error connecting to Sheet: {e}")
        return

    # 3. Upload Data
    try:
        # Prepare data: Header + Rows
        data_rows = [['id', 'json_data']]
        for c in local_data:
            j_str = json.dumps(c, ensure_ascii=False)
            data_rows.append([c['id'], j_str])
        
        # Clear and Update
        print("Clearing sheet...")
        ws.clear()
        print(f"Uploading {len(data_rows)-1} records...")
        ws.update('A1', data_rows) 
        print("Migration SUCCESS!")
    except Exception as e:
        print(f"Error uploading data: {e}")

if __name__ == "__main__":
    migrate_data()
