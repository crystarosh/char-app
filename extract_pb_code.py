
import os
import re

pb_path = r"C:\Users\sweet\.gemini\antigravity\conversations\e9b34a2c-98d0-48de-95e0-088596daa473.pb"

if not os.path.exists(pb_path):
    print(f"File not found: {pb_path}")
    exit(1)

print(f"Reading {pb_path}...")

# Read binary
try:
    with open(pb_path, 'rb') as f:
        data = f.read()
except Exception as e:
    print(f"Error reading file: {e}")
    exit(1)

# Extract strings (ASCII/UTF-8ish)
# Simple heuristic: sequence of printable chars > 20 length
import string
printable = set(string.printable.encode('ascii'))
# Allow some utf-8 bytes? Complex.
# Let's try to decode as utf-8 with errors='ignore' and thenregex search
text = data.decode('utf-8', errors='ignore')

print(f"Decoded length: {len(text)}")

# Look for 'generate_card_zip' definitions
matches = re.finditer(r'(def generate_card_zip.*?return b)', text, re.DOTALL)
found = False

for i, m in enumerate(matches):
    found = True
    code = m.group(1)
    # Check length to avoid fragments
    if len(code) > 500:
        print(f"\n--- FOUND BLOCK {i} (Len: {len(code)}) ---")
        # Print snippet or full if needed. 
        # Printing full might be large. I'll print full to capture "last known"
        print(code)
        
if not found:
    print("No 'def generate_card_zip' blocks found in extracted text.")
    # Try searching for specific coordinate changes if full block missing
    # e.g. "chart_y ="
    print("Searching for fragments...")
    frags = re.findall(r'(chart_y\s*=\s*\d+)', text)
    print(f"chart_y fragments: {frags}")
    
    frags2 = re.findall(r'(bio\s*=\s*char\.get)', text)
    print(f"bio fragments: {len(frags2)}")

