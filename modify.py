import os
import re
import shutil
import argparse

tasks_insertions = [(
r"import torch.nn as nn", True,
"""

from .moduleimplant import ModuleImplant"""
),(
r" +for i, \(f, n, m, args\)", False,
"""    globals().update(ModuleImplant.get_third_party_modules_dict())

"""
),(    
r"elif m is CBFuse:\s*c2 = ch\[f\[-1\]\]", True,
"""
        elif m in ModuleImplant.get_third_party_modules():
            c1, c2, args = ModuleImplant.parse_third_party_module(ch, f, n, m, args)"""
)]

init_insertions = [(
r"__all__", False,
"""from .moduleimplant import (
    ModuleImplant
)

"""
),(
r'"BaseModel",', True,
"""
    "ModuleImplant","""
)]

def insert_code(insertions: list, src: str, tar: str = None):
    with open(src, 'r') as f:
        content = f.read()
        
    for insert in insertions:
        match = re.search(insert[0], content)
        if match:
            insert_idx = match.end() if insert[1] else match.start()
            content = content[:insert_idx] + insert[2] + content[insert_idx:]
    if not tar:
        tar = src
        
    with open(tar, 'w') as f:
        f.write(content)

def modify(modify: bool):
    import ultralytics
    
    ultralytics_path = os.path.dirname(ultralytics.__file__)
    nn_modules_path = os.path.join(ultralytics_path, 'nn')
    
    if not os.path.isdir(nn_modules_path):
        raise AssertionError("Ultralytics does not have 'nn' dir as expected.")
    
    target_file = os.path.join(nn_modules_path, 'moduleimplant.py')
    source_file = os.path.join(os.path.dirname(__file__), 'moduleimplant.py')
    tasks_file = os.path.join(ultralytics_path, 'tasks.py')
    init_file = os.path.join(ultralytics_path, '__init__.py')
    
    if modify:
        # Copy moduleimplant.py to ultralytics/nn
        if os.path.isfile(source_file):
            shutil.copy(source_file, target_file)
            print(f"Successfully copied moduleimplant.py to '{target_file}'")
        else:
            raise FileNotFoundError("moduleimplant.py not found, skipping copy.")
        
        # Modify ultralytics inner file
        if os.path.isfile(tasks_file):
            shutil.copy(tasks_file, ".backup/tasks.py.bak")  # prep backup
            insert_code(tasks_insertions, tasks_file)
            print(f"Successfully modified {tasks_file}.")
        else:
            raise FileNotFoundError(f"{tasks_file} not found, skipping modification.")
        
        if os.path.isfile(init_file):
            shutil.copy(init_file, ".backup/__init__.py.bak")  # prep backup
            insert_code(init_insertions, init_file)
            print(f"Successfully modified {init_file}.")
        else:
            raise FileNotFoundError(f"{init_file} not found, skipping modification.")
    else:
        # Delete moduleimplant.py in Ultralytics pack
        if os.path.isfile(target_file):
            os.remove(target_file)
            print(f"Successfully delete '{target_file}'")
        else:
            raise FileNotFoundError("moduleimplant.py not found in Ultralytics, skipping delete.")
        # Check if backup is still remain, then copy back
        if os.path.isfile(".backup/tasks.py.bak"):
            shutil.copy(".backup/tasks.py.bak", tasks_file)
            print(f"Successfully recover '{tasks_file}'")
        else:
            raise FileNotFoundError(f"Backup of tasks.py not found, skipping recover.")
        if os.path.isfile(".backup/__init__.py.bak"):
            shutil.copy(".backup/__init__.py.bak", init_file)
            print(f"Successfully recover '{init_file}'")
        else:
            raise FileNotFoundError(f"Backup of __init__.py not found, skipping recover.")
        
parser = argparse.ArgumentParser(description="modify or de-modify Ultralytics with ModuleImplant")
parser.add_argument('command', choices=['modify', 'de-modify'], required=True)
            
def main():
    args = parser.parse_args()
    modify(args.command == 'modify')
        