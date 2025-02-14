"""
@author: prabinpebam
@title: anyPython v0.0.3
@nickname: anyPython
@description: This node can execute Python operations with user-confirmed risk management
"""

import numpy as np
from PIL import Image
import cv2
from typing import Dict, Any, Callable, Optional, Union, List
import inspect
import re
import importlib
import json
import tempfile
import os
import runpy
import sys
import io

class anyPython:
    # Dictionary of risky operations and their warning messages
    RISKY_OPERATIONS = {
        'os': {
            'risk_level': 'HIGH',
            'warning': 'This module can access and modify system files and directories',
            'operations': ['remove', 'rmdir', 'makedirs', 'system', 'popen', 'access']
        },
        'sys': {
            'risk_level': 'HIGH',
            'warning': 'This module can modify Python runtime environment',
            'operations': ['exit', 'modules', 'path']
        },
        'subprocess': {
            'risk_level': 'CRITICAL',
            'warning': 'This module can execute system commands',
            'operations': ['run', 'call', 'Popen']
        },
        'shutil': {
            'risk_level': 'HIGH',
            'warning': 'This module can perform file operations',
            'operations': ['rmtree', 'move', 'copy', 'copyfile']
        },
        'socket': {
            'risk_level': 'HIGH',
            'warning': 'This module can create network connections',
            'operations': ['socket', 'connect', 'bind', 'listen']
        },
        'requests': {
            'risk_level': 'MEDIUM',
            'warning': 'This module can make HTTP requests',
            'operations': ['get', 'post', 'put', 'delete']
        },
        'ctypes': {
            'risk_level': 'CRITICAL',
            'warning': 'This module can access system-level functions',
            'operations': ['windll', 'cdll', 'CDLL']
        },
        'urllib': {
            'risk_level': 'MEDIUM',
            'warning': 'This module can make network requests',
            'operations': ['urlopen', 'Request']
        },
        'sqlite3': {
            'risk_level': 'MEDIUM',
            'warning': 'This module can perform database operations',
            'operations': ['connect', 'execute']
        },
        'pickle': {
            'risk_level': 'HIGH',
            'warning': 'This module can deserialize Python objects (potential security risk)',
            'operations': ['load', 'loads']
        },
        'pptx': {
            'risk_level': 'LOW',
            'warning': 'This module can create and modify PowerPoint files',
            'operations': ['Presentation']
        },
        'win32api': {
            'risk_level': 'CRITICAL',
            'warning': 'This module can access Windows API functions',
            'operations': ['SendMessage', 'RegOpenKey']
        },
        'getpass': {
            'risk_level': 'MEDIUM',
            'warning': 'This module can access user information',
            'operations': ['getuser']
        }
    }

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "code": ("STRING", {"multiline": True, "default": "print(variable)"}),
                "confirm_risks": ("BOOLEAN", {"default": False, "label": "I understand and accept the risks"}),
            },
            "optional": {
                "variable": ("STRING", {"multiline": True, "default": "5"}),
                "image": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("STRING", "IMAGE",)
    FUNCTION = "execute_code"
    CATEGORY = "🚀 Any Python"

    def _analyze_code_risks(self, code: str) -> List[Dict[str, str]]:
        """Analyze code for potential risks"""
        risks = []
        
        # Check for imports
        import_pattern = r'^import\s+(\w+(?:\.\w+)*)|^from\s+(\w+(?:\.\w+)*)\s+import\s+(.+)$'
        for line in code.split('\n'):
            line = line.strip()
            match = re.match(import_pattern, line)
            if match:
                module_name = match.group(1) or match.group(2)
                base_module = module_name.split('.')[0]
                if base_module in self.RISKY_OPERATIONS:
                    risks.append({
                        'module': base_module,
                        'risk_level': self.RISKY_OPERATIONS[base_module]['risk_level'],
                        'warning': self.RISKY_OPERATIONS[base_module]['warning']
                    })

        # Check for risky operations
        for module, info in self.RISKY_OPERATIONS.items():
            for operation in info['operations']:
                if re.search(rf'\b{module}\.{operation}\b', code):
                    risks.append({
                        'module': module,
                        'operation': operation,
                        'risk_level': info['risk_level'],
                        'warning': info['warning']
                    })

        return risks

    def execute_code(self, code: str, confirm_risks: bool, variable: Optional[str] = None, image: Optional[np.ndarray] = None) -> tuple:
        """Execute code using a temporary module file and runpy.run_path for risk-free execution.
           Captures both explicit output variables and printed output.
        """
        try:
            # Analyze risks
            risks = self._analyze_code_risks(code)
            
            # If risks are found and not confirmed, return warning
            if risks and not confirm_risks:
                risk_message = "SECURITY RISKS DETECTED:\n\n"
                for risk in risks:
                    risk_message += f"⚠️ {risk['risk_level']} RISK: {risk['module']}\n"
                    risk_message += f"   Warning: {risk['warning']}\n"
                    if 'operation' in risk:
                        risk_message += f"   Risky operation detected: {risk['operation']}\n"
                risk_message += "\nTo proceed, please check 'I understand and accept the risks'"
                return risk_message, image

            # Set up an initial globals dictionary with provided inputs.
            globals_dict = {'variable': variable, 'image': image}
            
            # Process imports from the code
            import_pattern = r'^import\s+(\w+(?:\.\w+)*)|^from\s+(\w+(?:\.\w+)*)\s+import\s+(.+)$'
            for line in code.split('\n'):
                line = line.strip()
                match = re.match(import_pattern, line)
                if match:
                    try:
                        if match.group(1):  # Simple import
                            module_name = match.group(1)
                            globals_dict[module_name.split('.')[-1]] = importlib.import_module(module_name)
                        elif match.group(2) and match.group(3):  # From import
                            module_name = match.group(2)
                            imports = [i.strip() for i in match.group(3).split(',')]
                            module = importlib.import_module(module_name)
                            for imp in imports:
                                if imp == '*':
                                    continue  # Skip star imports
                                globals_dict[imp] = getattr(module, imp)
                    except ImportError as e:
                        return f"Import Error: {str(e)}", image

            # Write the user's code to a temporary Python file.
            with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as tmp_file:
                tmp_file.write(code)
                tmp_filename = tmp_file.name

            # Redirect stdout to capture printed output.
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()

            # Execute the temporary file as a module using runpy.
            result_globals = runpy.run_path(tmp_filename, init_globals=globals_dict)

            # Get any printed output.
            printed_output = sys.stdout.getvalue()
            sys.stdout = old_stdout

            # Clean up the temporary file.
            os.remove(tmp_filename)

            # Retrieve explicit output from the executed module.
            user_output = result_globals.get('output', None)
            # If no explicit output variable, use captured printed output.
            if user_output is None:
                user_output = printed_output.strip()
            
            # Retrieve image output from the executed module.
            result_image = result_globals.get('image', image)
            
            # If both outputs are empty, default to a success message.
            if not user_output and result_image is None:
                user_output = "Code executed successfully"
            
            return str(user_output), result_image
            
        except Exception as e:
            return f"Error: {str(e)}", image

# Node class mappings
NODE_CLASS_MAPPINGS = {
    "Any Python": anyPython
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Any Python": "anyPython"
}
