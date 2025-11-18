# smart_switch_factory.py
from typing import Any, Tuple, Dict, Optional, Union, Type

# Match your JS MAX_INPUTS (dynamic_inputs.js uses 8)
_MAX_INPUTS = 8


def _build_optional_inputs_dict(type_name: str) -> Dict[str, tuple]:
    """
    Helper function to build the dictionary of optional inputs for a switch node.

    This is where we dynamically create the input_1, input_2, etc. definitions
    for ComfyUI to use.
    """
    return {f"input_{i}": (type_name,) for i in range(1, _MAX_INPUTS + 1)}


def create_smart_switch_node(
    class_name: str,
    type_name: str,
    return_name: str,
    default_value: Any = None,
) -> Type:
    """
    Factory function to create a smart switch node class.

    I was getting tired of writing the same switch logic over and over for
    different data types (IMAGE, MODEL, etc.). This factory pattern solves that
    problem by generating the classes for me, so I only have to write the logic once.

    The smart switch node intelligently selects which input to pass through:
    1. If force_input_index > 0, tries that specific input first
    2. Otherwise, selects the first connected non-empty input
    3. Falls back to default_value if no valid input found

    For numeric types (INT/FLOAT), can optionally treat zero as empty.
    """

    def switch(self, **kwargs) -> Tuple[Any]:
        """
        Main switching logic for the node.

        This is the brain of the operation. It figures out which input to use
        based on the settings and what's actually connected.
        """
        # Extract and validate control parameters
        force_input_index = int(kwargs.get("force_input_index", 0))
        treat_zero_as_empty = bool(kwargs.get("treat_zero_as_empty", False))

        # Validate force_input_index
        if force_input_index < 0 or force_input_index > _MAX_INPUTS:
            print(
                f"WARNING: [Smart Switch] Invalid force_input_index {force_input_index}, using 0"
            )
            force_input_index = 0

        def is_effectively_empty(val: Any) -> bool:
            """
            Determine if a value should be considered "empty" for switching purposes.

            This is important because sometimes an input might be connected but
            have a default value that we don't want to use.
            """
            # Unconnected optionals aren't present in kwargs at all
            if val is None:
                return True

            # For numeric types, optionally treat zero as empty
            if type_name in ("INT", "FLOAT") and treat_zero_as_empty:
                try:
                    return float(val) == 0.0
                except (ValueError, TypeError):
                    return False

            # Empty string is considered empty
            if type_name == "STRING" and isinstance(val, str) and val == "":
                return True

            return False

        # 1) Try forced index first if specified
        if force_input_index > 0:
            key = f"input_{force_input_index}"
            if key in kwargs:
                v = kwargs[key]
                if not is_effectively_empty(v):
                    return (v,)
                else:
                    print(
                        f"WARNING: [Smart Switch] Forced input {force_input_index} is empty"
                    )

        # 2) Find first non-empty among connected inputs
        for i in range(1, _MAX_INPUTS + 1):
            key = f"input_{i}"
            if key in kwargs:
                v = kwargs[key]
                if not is_effectively_empty(v):
                    return (v,)

        # 3) Fallback to default value
        if default_value is not None:
            print(f"INFO: [Smart Switch] No valid input found, using default value")
        else:
            print(f"INFO: [Smart Switch] No valid input found, returning None")

        return (default_value,)

    @classmethod
    def INPUT_TYPES(cls):
        """Define the input types for the node."""
        req = {
            "force_input_index": (
                "INT",
                {
                    "default": 0,
                    "min": 0,
                    "max": _MAX_INPUTS,
                    "tooltip": "Force selection of specific input (0 = auto-select)",
                },
            ),
        }

        # Add zero-as-empty toggle for numeric types
        if type_name in ("INT", "FLOAT"):
            req["treat_zero_as_empty"] = (
                "BOOLEAN",
                {"default": False, "tooltip": "Treat 0/0.0 as empty value"},
            )

        return {
            "required": req,
            "optional": _build_optional_inputs_dict(type_name),
        }

    # Create the class attributes
    attrs = {
        "INPUT_TYPES": INPUT_TYPES,
        "RETURN_TYPES": (type_name,),
        "RETURN_NAMES": (return_name,),
        "FUNCTION": "switch",
        "CATEGORY": "EG Tools/Switch",
        "switch": switch,
        "DESCRIPTION": (
            f"Smart pass-through switch for {type_name} data. "
            "Selects first available data. You can force an input (0 = auto select). "
            + (
                "For INT/FLOAT, 'treat_zero_as_empty' can skip 0/0.0 as empty."
                if type_name in ("INT", "FLOAT")
                else ""
            )
        ),
    }

    # Create and return the new class
    return type(class_name, (object,), attrs)
