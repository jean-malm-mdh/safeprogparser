import sys
import os

module_name = os.path.dirname(os.path.abspath(__file__))
top_path = os.path.join(module_name, "..")
if not top_path in sys.path:
    sys.path.append(module_name)
    sys.path.append(top_path)
from parser import Rectangle
from parser import Point
