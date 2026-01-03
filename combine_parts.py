
import os

parts = ["part1a.py", "part1b.py", "part2.py", "part3.py"]
output_file = "char_app.py"

with open(output_file, "w", encoding="utf-8") as outfile:
    # Optional: Write encoding declaration just in case, though standard UTF-8 doesn't strictly need it in Py3
    # outfile.write("# -*- coding: utf-8 -*-\n") 
    
    for part in parts:
        if os.path.exists(part):
            with open(part, "r", encoding="utf-8") as infile:
                outfile.write(infile.read())
            outfile.write("\n") # Ensure newline between parts
        else:
            print(f"Warning: {part} not found")

print(f"Successfully combined {parts} into {output_file}")
