# Re-export from Error-Codes for Python-compatible import path
from importlib import import_module as _im
import sys as _sys

_mod = _im("Src.Error-Codes.exceptions")
_sys.modules[__name__ + ".exceptions"] = _mod
