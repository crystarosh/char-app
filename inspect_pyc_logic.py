
import marshal
import dis
import sys

pyc_path = r'__pycache__/char_app.cpython-310.pyc'

try:
    with open(pyc_path, 'rb') as f:
        f.read(16)
        code_obj = marshal.load(f)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)

def find_inner_functions(code):
    funcs = {}
    for const in code.co_consts:
        if isinstance(const, type(code)):
            funcs[const.co_name] = const
            funcs.update(find_inner_functions(const))
    return funcs

all_funcs = find_inner_functions(code_obj)
target_func_name = 'create_card_2'

if target_func_name in all_funcs:
    target = all_funcs[target_func_name]
    print(f"--- Constants in {target_func_name} ---")
    for i, c in enumerate(target.co_consts):
        print(f"{i}: {c}")
    
    print(f"\n--- Disassembly of {target_func_name} ---")
    dis.dis(target)
else:
    print(f"{target_func_name} not found.")
    print("Available functions:", list(all_funcs.keys()))

target_func_name = 'create_card_3'
if target_func_name in all_funcs:
    target = all_funcs[target_func_name]
    print(f"\n--- Constants in {target_func_name} ---")
    for i, c in enumerate(target.co_consts):
        print(f"{i}: {c}")
