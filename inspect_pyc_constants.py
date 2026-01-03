
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
targets = ['create_card_2', 'create_card_3']

for t in targets:
    if t in all_funcs:
        code = all_funcs[t]
        print(f"=== {t} Constants ===")
        for c in code.co_consts:
            if isinstance(c, (int, str, tuple)):
                print(c)
    else:
        print(f"=== {t} NOT FOUND ===")
