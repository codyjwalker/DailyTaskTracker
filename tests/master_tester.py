# tests/master_tester.py
import sys
import os
import importlib
import traceback

# Add the project root to sys.path
root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, root)

# Find all test modules under the tests directory
import glob

test_dir = os.path.join(root, 'tests')
pattern = os.path.join(test_dir, 'test_*.py')
all_tests = sorted(glob.glob(pattern))
# Exclude this master tester itself
master = os.path.abspath(__file__)
modules = [t for t in all_tests if os.path.abspath(t) != master]


total = 0
passed = 0
print('Running master test suite:')
for file_path in modules:
    mod_name = os.path.splitext(os.path.basename(file_path))[0]
    try:
        mod = importlib.import_module(mod_name)
    except Exception as e:
        print(f'[{mod_name}] ImportError: {e}')
        continue
    for attr in dir(mod):
        if attr.startswith('test_'):
            total += 1
            func = getattr(mod, attr)
            try:
                func()
                print(f'[{mod_name}.{attr}] PASS')
                passed += 1
            except AssertionError as e:
                print(f'[{mod_name}.{attr}] FAIL: {e}')
            except Exception as e:
                print(f'[{mod_name}.{attr}] ERROR: {e}')
                traceback.print_exc()
print(f'\n{passed}/{total} tests passed.')
