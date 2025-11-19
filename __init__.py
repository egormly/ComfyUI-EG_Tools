# __init__.py for EG_Tools
import os

# ------------------------------------------------------------------------------
# 1. IMPORT WRAPPERS
# ------------------------------------------------------------------------------
from .eg_save_image import (
    NODE_CLASS_MAPPINGS as SAVE_CLASS,
    NODE_DISPLAY_NAME_MAPPINGS as SAVE_DISPLAY,
)
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
from .eg_checkpoint import (
    NODE_CLASS_MAPPINGS as CHECK_CLASS,
    NODE_DISPLAY_NAME_MAPPINGS as CHECK_DISPLAY,
)

from .visual_image_loader import (
    NODE_CLASS_MAPPINGS as LOADER_CLASS,
    NODE_DISPLAY_NAME_MAPPINGS as LOADER_DISPLAY,
)

# ------------------------------------------------------------------------------
# 2. MAPPINGS
# ------------------------------------------------------------------------------

NODE_CLASS_MAPPINGS = {
    **SAVE_CLASS,
    **INFO_CLASS,
    **PATHS_CLASS,
    **SWITCHES_CLASS,
    **CHECK_CLASS,
    **LOADER_CLASS,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    **INFO_DISPLAY,
    **PATHS_DISPLAY,
    **SWITCHES_DISPLAY,
    **SAVE_DISPLAY,
    **CHECK_DISPLAY,
    **LOADER_DISPLAY,
}


# ------------------------------------------------------------------------------
# 3. CONFIGURATION
# ------------------------------------------------------------------------------

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
