# smart_switches.py
# This file uses the factory to generate all the individual Smart Switch nodes
# and registers them with ComfyUI so they show up in the menu.

import os
import sys
from typing import Dict, Any

# Keep imports robust whether this dir is a package or flat
# Add the current directory to Python's path if it's not already there
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Try different import methods
try:
    from .smart_switch_factory import create_smart_switch_node  # type: ignore
except ImportError:
    try:
        from smart_switch_factory import create_smart_switch_node  # type: ignore
    except ImportError as e:
        print(f"Error importing smart_switch_factory: {e}")
        print(
            "Make sure smart_switch_factory.py is in the same directory as smart_switches.py"
        )
        raise

# This is the central configuration for all the switch types we want to create.
# To add a new switch type, just add an entry here.
SWITCH_TYPES = {
    "INT": {
        "return_name": "int",
        "default": None,
        "description": "Switch for integer values",
    },
    "FLOAT": {
        "return_name": "float",
        "default": 0.0,
        "description": "Switch for floating-point values",
    },
    "STRING": {
        "return_name": "text",
        "default": "",
        "description": "Switch for text strings",
    },
    "TEXT": {
        "return_name": "text",
        "default": "",
        "description": "Switch for text data",
    },
    "IMAGE": {
        "return_name": "image",
        "default": None,
        "description": "Switch for image tensors",
    },
    "CONDITIONING": {
        "return_name": "conditioning",
        "default": None,
        "description": "Switch for conditioning data",
    },
    "MODEL": {
        "return_name": "model",
        "default": None,
        "description": "Switch for diffusion models",
    },
    "VAE": {
        "return_name": "vae",
        "default": None,
        "description": "Switch for VAE models",
    },
    "LATENT": {
        "return_name": "latent",
        "default": None,
        "description": "Switch for latent samples",
    },
    "CLIP": {
        "return_name": "clip",
        "default": None,
        "description": "Switch for CLIP models",
    },
    "CONTROL_NET": {
        "return_name": "control_net",
        "default": None,
        "description": "Switch for ControlNet models",
    },
    "UPSCALE_MODEL": {
        "return_name": "upscale_model",
        "default": None,
        "description": "Switch for upscaling models",
    },
}

# Initialize mappings for ComfyUI registration
NODE_CLASS_MAPPINGS: Dict[str, Any] = {}
NODE_DISPLAY_NAME_MAPPINGS: Dict[str, str] = {}

# This is where the magic happens! We loop through our config and use the
# factory to create a new class for each switch type. Then we register it
# with ComfyUI so it appears in the node menu.
for type_name, config in SWITCH_TYPES.items():
    # Create a unique class name, e.g., "EG_SmartSwitch_IMAGE"
    class_name = f"EG_SmartSwitch_{type_name}"

    # Create a user-friendly display name, e.g., "EG Smart Switch (IMAGE)"
    display_name = f"EG Smart Switch ({type_name})"

    # Generate the node class using the factory
    NodeClass = create_smart_switch_node(
        class_name=class_name,
        type_name=type_name,
        return_name=config["return_name"],
        default_value=config["default"],
    )

    # Add description if provided
    if "description" in config:
        NodeClass.DESCRIPTION = config["description"]

    # Register the node so ComfyUI can see it
    NODE_CLASS_MAPPINGS[class_name] = NodeClass
    NODE_DISPLAY_NAME_MAPPINGS[class_name] = display_name

# Export the mappings for ComfyUI
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
