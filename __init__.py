# __init__.py for EG_Tools
import os

# ------------------------------------------------------------------------------
# 1. IMPORT WRAPPERS
# ------------------------------------------------------------------------------

from .eg_image_info import (
    NODE_CLASS_MAPPINGS as INFO_CLASS,
    NODE_DISPLAY_NAME_MAPPINGS as INFO_DISPLAY,
)
from .eg_project_paths import (
    NODE_CLASS_MAPPINGS as PATHS_CLASS,
    NODE_DISPLAY_NAME_MAPPINGS as PATHS_DISPLAY,
)
from .smart_switches import (
    NODE_CLASS_MAPPINGS as SWITCHES_CLASS,
    NODE_DISPLAY_NAME_MAPPINGS as SWITCHES_DISPLAY,
)


NODE_CLASS_MAPPINGS = {
    **INFO_CLASS,
    **PATHS_CLASS,
    **SWITCHES_CLASS,
    # **GATE_CLASS,  # Uncomment this if you use smart_gate
}

NODE_DISPLAY_NAME_MAPPINGS = {
    **INFO_DISPLAY,
    **PATHS_DISPLAY,
    **SWITCHES_DISPLAY,
    # **GATE_DISPLAY, # Uncomment this if you use smart_gate
}


# ------------------------------------------------------------------------------
# 3. CONFIGURATION
# ------------------------------------------------------------------------------

# Tell ComfyUI to serve the "web" folder (for your custom Javascript)
WEB_DIRECTORY = "web"

# This is the list of variables that ComfyUI will import from this file
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]


# ------------------------------------------------------------------------------
# 4. CONSOLE OUTPUT
# ------------------------------------------------------------------------------
print(
    f"🛠️  [EG_Tools] Loaded {len(NODE_CLASS_MAPPINGS)} nodes successfully.\n"
    r" __ __   ___ _  _     __"
    "\n"
    r"|_ /__    | / \/ \|  (_"
    "\n"
    r"|__\_|    | \_/\_/|____)"
    "\n"
)
