
import sys
import os
from PIL import Image

# Mock classes
class MockManager:
    characters = []

# Mock Char
char = {
    'id': 'test',
    'name': 'Test Character',
    'first_name': 'Test',
    'last_name': 'Char',
    'user_name': 'tester',
    'images': [],
    'details': {
        'race': '人間',
        'role': 'Warrior',
        'height_weight': '170cm/60kg',
        'origin': 'City',
        'age': '20',
        'eye_color': '#FF0000',
        'hair_color': '#0000FF',
        'image_color': '#00FF00',
        'memo': 'Short memo'
    },
    'stats': {},
    'personality_stats': {},
    'bio': 'Test bio',
    'relations': []
}
manager = MockManager()

print("Importing char_app...")
try:
    import char_app
except ImportError:
    # If standard import fails due to streamlit dependency issues in CLI
    pass

# We might need to mock streamlit if char_app imports it at top level
import unittest.mock
sys.modules['streamlit'] = unittest.mock.MagicMock()
sys.modules['streamlit.components.v1'] = unittest.mock.MagicMock()

# Now import
if 'char_app' in sys.modules: del sys.modules['char_app']
import char_app

print("Running generate_card_zip...")
try:
    res = char_app.generate_card_zip(char, manager)
    if res:
        print("Success! Data length:", len(res.getvalue()))
    else:
        print("Returned None (Failure caught inside function)")
except Exception as e:
    print(f"Crashed with: {e}")
    import traceback
    traceback.print_exc()
