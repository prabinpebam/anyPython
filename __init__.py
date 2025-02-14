"""Top-level package for anyPython."""

__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS",
    "WEB_DIRECTORY",
]

__author__ = """Prabin Pebam"""
__email__ = "prabinpebam@gmail.com"
__version__ = "0.0.2"

from .src.anypython.nodes import NODE_CLASS_MAPPINGS
from .src.anypython.nodes import NODE_DISPLAY_NAME_MAPPINGS

WEB_DIRECTORY = "./web"
