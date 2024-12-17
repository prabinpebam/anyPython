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
import datetime

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

class anyPython:     

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {       
                    "code": ("STRING", {"multiline": True, "default": "print(variable)"}),                              
                    },
                "optional": {   
                    "variable": ("STRING", {"multiline": True, "default": "5"}),
                    "image": ("IMAGE",),            
                    },
                }

    # Define the return type as a tuple with both STRING and IMAGE
    RETURN_TYPES = ("STRING", "IMAGE")
    FUNCTION = "execute_code"
    CATEGORY = "🚀 Any Python"

    def execute_code(self, code, variable=None, image=None):
        # Redirect stdout to capture print statements
        old_stdout = sys.stdout
        redirected_output = sys.stdout = StringIO()

        # Create a local dictionary to hold the variables
        local_vars = {"variable": variable}

        # Include the image in local_vars if it's provided
        if image is not None:
            local_vars["image"] = image

        try:
            # Execute the Python code safely within the local scope
            exec(code, {}, local_vars)
        except Exception as e:
            # Return the error message and None for the image
            return (str(e), None)
        finally:
            # Restore stdout
            sys.stdout = old_stdout

        # Get the output and return it along with the image as a tuple
        output = redirected_output.getvalue()
        return (output, image)
