# __init__.py for EG_Tools

import os
import importlib.util
import sys

# Tell ComfyUI that the "web" subfolder should be served publicly
WEB_DIRECTORY = "web"

# Get the directory of the current script (__init__.py)
NODE_DIR = os.path.dirname(os.path.abspath(__file__))

# These will hold all the node mappings from all files
NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

# Explicitly import each module to ensure proper registration
MODULES = [
    "eg_image_info",
    "eg_project_paths",
    "smart_gate",
    "smart_switches",
    "smart_switch_factory",
]

# First import the factory module since others depend on it
try:
    spec = importlib.util.spec_from_file_location(
        "smart_switch_factory", os.path.join(NODE_DIR, "smart_switch_factory.py")
    )
    factory_module = importlib.util.module_from_spec(spec)
    sys.modules["smart_switch_factory"] = factory_module
    spec.loader.exec_module(factory_module)
    print(f"[EG_Tools] Loaded smart_switch_factory module")
except Exception as e:
    print(f"[EG_Tools] Error loading smart_switch_factory: {e}")

# Now import the rest of the modules
for module_name in MODULES:
    if module_name == "smart_switch_factory":
        continue  # Already loaded above

    module_path = os.path.join(NODE_DIR, f"{module_name}.py")

    # Skip if the file doesn't exist
    if not os.path.exists(module_path):
        print(f"[EG_Tools] Module file not found: {module_path}")
        continue

    try:
        # Import the module dynamically
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        # Check if the module has the required mappings and merge them
        if hasattr(module, "NODE_CLASS_MAPPINGS"):
            NODE_CLASS_MAPPINGS.update(module.NODE_CLASS_MAPPINGS)
            print(
                f"[EG_Tools] Loaded nodes from {module_name}: {list(module.NODE_CLASS_MAPPINGS.keys())}"
            )

        if hasattr(module, "NODE_DISPLAY_NAME_MAPPINGS"):
            NODE_DISPLAY_NAME_MAPPINGS.update(module.NODE_DISPLAY_NAME_MAPPINGS)

    except Exception as e:
        print(f"[EG_Tools] Error loading module {module_name}: {e}")

# Try to load documentation if available
try:
    from . import documentation

    documentation.add_documentation(NODE_CLASS_MAPPINGS)
    print("[EG_Tools] Documentation loaded successfully.")
except ImportError:
    print("[EG_Tools] documentation.py not found, skipping documentation.")

# This is what ComfyUI looks for
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]

print(
    f"🛠️🛠️🛠️🛠️ [EG_Tools] All nodes loaded successfully. 🛠️🛠️🛠️🛠️ Total nodes: {len(NODE_CLASS_MAPPINGS)}.\n"
    r" __ __   ___ _  _     __"
    "\n"
    r"|_ /__    | / \/ \|  (_"
    "\n"
    r"|__\_|    | \_/\_/|____)"
    "\n"
)
