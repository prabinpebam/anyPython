"""
@author: prabinpebam
@title: AnyPython v0.1
@nickname: AnyPython
@description: This node can take any input and use that to run a python script in ComfyUI
"""

# Import common libs
import sys
from io import StringIO

# Import html formatting stuff
from bs4 import BeautifulSoup
from prettytable import PrettyTable

# Import Additional common libs
import os, json, random, string, sys, math, datetime, collections, itertools, functools, urllib, shutil, re, torch, time, decimal, matplotlib, io, base64, wave, chromadb, uuid, scipy, torchaudio, torchvision, cv2, PIL
import numpy
import numpy as np
import torch.nn.functional as F
from torchvision import transforms
from sklearn.cluster import KMeans
import collections.abc
import traceback
import os
import pkgutil
import importlib

import re


class anyPythonZeroinput:     

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {       
                    "code": ("STRING", {"multiline": True, "default": "print('Hello, World!')"}),
                    }
                }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "execute_code"
    CATEGORY = "🚀 Any Python"

    def execute_code(self, code):        

        # Redirect stdout to capture print statements
        old_stdout = sys.stdout
        redirected_output = sys.stdout = StringIO()
        
        try:
            # Execute the Python code safely
            exec(code)
        except Exception as e:
            return (str(e),)
        finally:
            # Restore stdout
            sys.stdout = old_stdout
        
        # Get the output and return it as a tuple
        output = redirected_output.getvalue()
        return (output,)

        
class anyPythonOneInput:     

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {       
                    "code": ("STRING", {"multiline": True, "default": "print(variable)"}),                    
                    "variable": ("STRING", {"multiline": True, "default": "5"}),             
                    }
                }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "execute_code"
    CATEGORY = "🚀 Any Python"

    def execute_code(self, code, variable):
        # Redirect stdout to capture print statements
        old_stdout = sys.stdout
        redirected_output = sys.stdout = StringIO()
        
        # Create a local dictionary to hold the variable
        local_vars = {"variable": variable}
        
        try:
            # Execute the Python code safely within the local scope
            exec(code, {}, local_vars)
        except Exception as e:
            return (str(e),)
        finally:
            # Restore stdout
            sys.stdout = old_stdout
        
        # Get the output and return it as a tuple
        output = redirected_output.getvalue()
        return (output,)


class anyPythonTwoInputs:     

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {       
                    "code": ("STRING", {"multiline": True, "default": "print(variable1, variable2)"}),                    
                    "variable1": ("STRING", {"multiline": True, "default": "5"}),             
                    "variable2": ("STRING", {"multiline": True, "default": "10"}),             
                    }
                }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "execute_code"
    CATEGORY = "🚀 Any Python"

    def execute_code(self, code, variable1, variable2):
        # Redirect stdout to capture print statements
        old_stdout = sys.stdout
        redirected_output = sys.stdout = StringIO()
        
        # Create a local dictionary to hold the variables
        local_vars = {"variable1": variable1, "variable2": variable2}
        
        try:
            # Execute the Python code safely within the local scope
            exec(code, {}, local_vars)
        except Exception as e:
            return (str(e),)
        finally:
            # Restore stdout
            sys.stdout = old_stdout
        
        # Get the output and return it as a tuple
        output = redirected_output.getvalue()
        return (output,)
