# eg_save_image.py

import os
import json
import shutil
import random
import numpy as np
from PIL import Image
from PIL.PngImagePlugin import PngInfo
import folder_paths


class EG_SaveImage:
    """
    The 'No Compromises' Save Node.
    1. Respects exact filenames.
    2. Defaults to 'output/' folder for relative paths.
    3. ALWAYS shows a preview (even if saving to external drives).
    4. Auto-detects format (PNG/JPG/WEBP).
    """

    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
        self.temp_dir = folder_paths.get_temp_directory()
        self.type = "output"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE",),
                "filename": (
                    "STRING",
                    {"default": "MyImages/Image.png", "multiline": False},
                ),
            },
            "optional": {
                "quality": (
                    "INT",
                    {
                        "default": 100,
                        "min": 1,
                        "max": 100,
                        "step": 1,
                        "tooltip": "JPEG/WEBP Quality",
                    },
                ),
                "embed_workflow": (
                    "BOOLEAN",
                    {"default": True, "tooltip": "Save metadata (PNG Only)"},
                ),
            },
            "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"},
        }

    RETURN_TYPES = ()
    FUNCTION = "save_images"
    OUTPUT_NODE = True
    CATEGORY = "EG Tools/Image"
    DESCRIPTION = "Saves to exact path. Relative paths go to 'output/'. Absolute paths go anywhere. Always displays preview. Careful - will overwrite exiting images!"

    def save_images(
        self,
        images,
        filename,
        quality=100,
        embed_workflow=True,
        prompt=None,
        extra_pnginfo=None,
    ):

        # 1. Resolve the Path
        filename = filename.strip()
        if not filename:
            filename = "Untitled.png"

        # Check if path is absolute (C:/... or /home/...)
        # If not, prepend the ComfyUI output directory
        if os.path.isabs(filename):
            full_path = filename
        else:
            full_path = os.path.join(self.output_dir, filename)

        # Create the destination folder if it doesn't exist
        directory = os.path.dirname(full_path)
        if directory and not os.path.exists(directory):
            try:
                os.makedirs(directory, exist_ok=True)
            except Exception as e:
                print(f"[EG_Tools] Error creating directory {directory}: {e}")
                return {}

        # 2. Determine Format based on extension
        ext = os.path.splitext(full_path)[1].lower()
        if not ext:
            ext = ".png"
            full_path += ".png"

        format_map = {".png": "PNG", ".jpg": "JPEG", ".jpeg": "JPEG", ".webp": "WEBP"}
        pil_format = format_map.get(ext, "PNG")

        # 3. Prepare Metadata
        metadata = None
        if embed_workflow and pil_format == "PNG":
            metadata = PngInfo()
            if prompt is not None:
                metadata.add_text("prompt", json.dumps(prompt))
            if extra_pnginfo is not None:
                for x in extra_pnginfo:
                    metadata.add_text(x, json.dumps(extra_pnginfo[x]))

        # 4. Save Images & Generate Previews
        results = list()

        for i, image in enumerate(images):
            # Convert Tensor to PIL
            i_255 = 255.0 * image.cpu().numpy()
            img = Image.fromarray(np.clip(i_255, 0, 255).astype(np.uint8))

            # Handle Batch Naming (append _01 if batch > 1)
            current_full_path = full_path
            if len(images) > 1:
                base, extension = os.path.splitext(full_path)
                current_full_path = f"{base}_{i+1:02d}{extension}"

            # --- SAVE THE ACTUAL FILE ---
            try:
                if pil_format == "PNG":
                    img.save(current_full_path, pnginfo=metadata, optimize=True)
                elif pil_format == "JPEG":
                    img.save(current_full_path, quality=quality, optimize=True)
                elif pil_format == "WEBP":
                    img.save(
                        current_full_path, quality=quality, lossless=(quality == 100)
                    )

                print(f"[EG_Tools] Saved: {current_full_path}")
            except Exception as e:
                print(f"[EG_Tools] Failed to save {current_full_path}: {e}")
                continue

            # --- HANDLE PREVIEW ---
            # Case A: We are saving inside the standard 'output' folder.
            # ComfyUI can serve this directly if we give it the relative subfolder.
            if (
                os.path.commonpath(
                    [self.output_dir, os.path.abspath(current_full_path)]
                )
                == self.output_dir
            ):
                # Calculate relative path for the UI
                relative_path = os.path.relpath(current_full_path, self.output_dir)
                subfolder = os.path.dirname(relative_path)
                filename_only = os.path.basename(relative_path)

                results.append(
                    {
                        "filename": filename_only,
                        "subfolder": subfolder,
                        "type": "output",
                    }
                )

            # Case B: We are saving to an external drive / weird location.
            # ComfyUI web server CANNOT serve C:/Images directly.
            # Fix: Save a temporary copy to 'temp/' so the UI has something to show.
            else:
                # Create a unique temp filename to avoid collisions
                temp_filename = f"preview_{random.randint(100000, 999999)}_{os.path.basename(current_full_path)}"
                if not temp_filename.lower().endswith(".png"):
                    temp_filename += ".png"  # Force PNG for reliable previews

                temp_path = os.path.join(self.temp_dir, temp_filename)

                # Save a quick copy for preview (always PNG for safety)
                img.save(temp_path, compress_level=1)  # Fast save

                results.append(
                    {"filename": temp_filename, "subfolder": "", "type": "temp"}
                )

        return {"ui": {"images": results}}


# Register
NODE_CLASS_MAPPINGS = {"EG_SaveImage": EG_SaveImage}

NODE_DISPLAY_NAME_MAPPINGS = {"EG_SaveImage": "Save Image (Exact Path)"}
