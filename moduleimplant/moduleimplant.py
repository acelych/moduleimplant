import os
import sys
import pickle
import atexit
import inspect
import importlib.util

class ModuleImplant():
    '''
    This project can help you implant 3rd party / custom pytorch nn.module components
    into Ultralytics library. After that, you can simply modify the yaml file,
    which defines your network structure, with new components.
    
    Paste this .py file where task.py located, modify task.py as following:
    1. import
        ```python
        from .moduleimplant import ModuleImplant
        ```
    2. update globals() during parse_model()
        ```python
        globals().update(ModuleImplant.get_third_party_modules_dict())
        # insert this before 'for i, (f, n, m, args) in enumerate...'
        ```
    3. add this elif within others in the for statement that mentioned above
        ```python
        elif m in ModuleImplant.get_third_party_modules():
            c1, c2, args = ModuleImplant.parse_third_party_module(ch, f, n, m, args)
        ```
        
    Then, modify the paralled __init__.py file as following:
    1. add this piece of code
        ```python
        from .moduleimplant import (
            ModuleImplant
        )
        ```
    2. add "ModuleImplant" to __all__
    
    You also need a parser func to parse arguments provided by .yaml file.
    Implement a func called 'yaml_args_parser' in your custom module like this:
    ```python
    @staticmethod
    def yaml_args_parser(ch, f, n, m, args):
        return ch[f], ch[f], [ch[f], *args]
    ```
    tasks.py will pass 5 arguments for your custom module:
    - ch: a list that recorded all layers' output channel count
    - f: previous layer's serial number which indicates where this layer's data comes from
    - n: assume that your layer should be a serial of modules, n represents the repetition times
    - m: definition form of this module
    - args: custom arguments after aboves
    tasks.py needs 3 return values:
    - c1: layer's input channel count
    - c2: layer's output channel count
    - args: all arguments that module's initial function requires
    '''
    
    from torch.nn import Module
    from typing import List, Dict, Any, Union, Callable, Type

    _module_collect = {}
    _module_implant_dir = os.path.dirname(os.path.abspath(__file__))
    _module_implant_tmppkl = os.path.join(_module_implant_dir, "moduleimplant_tmp.pkl")

    @classmethod
    def _clean_tmppkl(cls):
        if os.path.isfile(cls._module_implant_tmppkl):
            os.remove(cls._module_implant_tmppkl)
    
    @classmethod
    def _save_dict(cls):
        with open(cls._module_implant_tmppkl, 'wb') as f:
            pickle.dump(list(cls._module_collect.values()), f)

    @classmethod
    def _load_dict(cls):
        if not os.path.isfile(cls._module_implant_tmppkl):
            cls._module_collect.clear()
            return
        
        with open(cls._module_implant_tmppkl, 'rb') as f:
            saved_dict = {}
            for path, module_name, class_name in pickle.load(f):
                
                spec = importlib.util.spec_from_file_location(module_name, path)
                module = importlib.util.module_from_spec(spec)
                
                if module_name not in sys.modules:                    
                    sys.modules[module_name] = module
                    spec.loader.exec_module(module)
                    saved_dict[getattr(module, class_name)] = (path, module_name, class_name)
                    
            cls._module_collect.update(saved_dict)

    @classmethod
    def add_third_party_module(cls, modules: Union[Module, List[Module]]) -> None:
        if not isinstance(modules, list):
            modules = [modules]
        for module in modules:
            if not hasattr(module, 'yaml_args_parser'):
                raise NotImplementedError(f"Module '{module}' does not implement 'yaml_args_parser' for Ultralytics.")
            cls._module_collect[module] = (
                inspect.getabsfile(module),     # absolute path to .py file
                module.__module__,              # module (in python definition) name
                module.__name__,                # module (pytorch nn.Module) name (aka class name)
            )
        cls._save_dict()
    
    @classmethod
    def get_third_party_modules_dict(cls) -> Dict[str, Module]:
        cls._load_dict()
        return {m.__name__: m for m in cls._module_collect.keys()}
    
    @classmethod
    def get_third_party_modules(cls) -> list[Module]:
        cls._load_dict()
        return list(cls._module_collect.keys())
    
    @classmethod
    def parse_third_party_module(cls, 
                                 channels: Any,
                                 former: int, num: int, 
                                 module: Union[Type[Module], str],
                                 args: Any) -> tuple:
        '''
        Called when tasks.py need a guideline to process a set of module arguments
        '''
        if isinstance(module, str):
            matched_module = next((m for m in cls._module_collect.keys() if m.__name__ == module), None)
            if matched_module:
                module = matched_module
            else:
                raise KeyError(f"Could not find \"{module}\" in modules collection.")
        if module in cls._module_collect.keys():
            return module.yaml_args_parser(channels, former, num, module, args)
        
atexit.register(ModuleImplant._clean_tmppkl)