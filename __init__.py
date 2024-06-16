from .nodes.nodes import *

NODE_CLASS_MAPPINGS = { 
    "Any Python no input": anyPythonZeroinput,
    "Any Python 1 input": anyPythonOneInput,
    "Any Python 2 input": anyPythonTwoInputs,
    
    }
    
print("\033[34mConfyUI AnyPython: \033[92mLoaded\033[0m")
