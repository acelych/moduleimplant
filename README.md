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