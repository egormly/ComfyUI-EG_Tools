import os
from pathlib import Path
from datetime import datetime
from typing import Tuple
import folder_paths


class EG_ProjectRoot:
    """Set the root folder for your entire project — everything else builds on this."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "base_folder": (
                    "STRING",
                    {
                        "default": "MyProjects",
                        "multiline": False,
                        "tooltip": "Top-level folder (created inside ComfyUI/output if relative)",
                    },
                ),
                "project_name": (
                    "STRING",
                    {
                        "default": "New_Project",
                        "multiline": False,
                        "tooltip": "Name of this specific project/run",
                    },
                ),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("project_root",)
    FUNCTION = "get_root"
    CATEGORY = "EG Tools/Paths"

    def get_root(self, base_folder: str, project_name: str) -> Tuple[str]:
        if not base_folder or not project_name:
            raise ValueError("Both base_folder and project_name are required")

        project_name = "".join(
            c for c in project_name if c.isalnum() or c in " _-"
        ).strip()
        if not project_name:
            project_name = "Untitled"

        path = Path(base_folder) / project_name / ""
        return (str(path).replace("\\", "/"),)


class EG_PathIndexPrefix:
    """Build only the slot prefix (e.g. Image03_) — use when letting ComfyUI auto-number the counter."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "project_root": ("STRING", {}),
                "slot_index": (
                    "INT",
                    {
                        "default": 1,
                        "min": 1,
                        "max": 999,
                        "step": 1,
                        "tooltip": "Slot number (01-99). Use different slots for different output types:\n"
                        "01 = final images, 02 = grids, 03 = raw latents, etc.",
                    },
                ),
                "name_prefix": (
                    "STRING",
                    {
                        "default": "Image",
                        "multiline": False,
                        "tooltip": "Descriptive name for this slot (e.g. Final, Upscale, Mask)",
                    },
                ),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("filename_prefix",)
    FUNCTION = "get_prefix"
    CATEGORY = "EG Tools/Paths"

    def get_prefix(
        self, project_root: str, slot_index: int, name_prefix: str
    ) -> Tuple[str]:
        if not project_root or not name_prefix:
            raise ValueError("project_root and name_prefix are required")
        if not 1 <= slot_index <= 999:
            raise ValueError("slot_index must be 1-999")

        safe_prefix = "".join(
            c for c in name_prefix if c.isalnum() or c in " _-"
        ).strip()
        if not safe_prefix:
            safe_prefix = "Image"

        slot_str = f"{slot_index:02d}"
        prefix = Path(project_root) / f"{safe_prefix}{slot_str}_"
        return (str(prefix).replace("\\", "/"),)


class EG_PathIndexFilename:
    """Build the EXACT filename ComfyUI Save Image uses: Slot__Counter_Ext
    Perfect for re-loading a specific generation later (e.g. you regenerated image #27).
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "project_root": ("STRING", {"default": "MyProjects/New_Project"}),
                "slot_index": (
                    "INT",
                    {
                        "default": 1,
                        "min": 1,
                        "max": 999,
                        "step": 1,
                        "tooltip": "Same slot as in 'Build Prefix' — groups images by type (01-99)",
                    },
                ),
                "name_prefix": (
                    "STRING",
                    {
                        "default": "Image",
                        "multiline": False,
                        "tooltip": "Same name as in 'Build Prefix' (e.g. Final, Grid)",
                    },
                ),
                "image_index": (
                    "INT",
                    {
                        "default": 1,
                        "min": 1,
                        "max": 999999,
                        "step": 1,
                        "tooltip": "Exact counter of the image you want.\n"
                        "ComfyUI numbers sequentially: 00001, 00002, etc.\n"
                        "If you re-run a single slot to replace image #27 → set this to 27",
                    },
                ),
                "extension": (
                    "STRING",
                    {
                        "default": ".png",
                        "multiline": False,
                        "tooltip": "File extension including the dot. Default .png works perfectly",
                    },
                ),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("filepath",)
    FUNCTION = "build_path"
    CATEGORY = "EG Tools/Paths"
    DESCRIPTION = (
        "Creates the exact filename ComfyUI Save Image would create.\n\n"
        "Example: slot_index=3 + image_index=27 → Image03__00027_.png\n\n"
        "Use this node when you need to:\n"
        "• Hard-load a specific image later (e.g. after regenerating #27)\n"
        "• Build automatic upscale/refine loops\n"
        "• Know exactly which file belongs to which generation\n\n"
        "Use 'Build Prefix' instead when you want ComfyUI to auto-increment."
    )

    def build_path(
        self,
        project_root: str,
        slot_index: int,
        name_prefix: str,
        image_index: int,
        extension: str,
    ) -> Tuple[str]:

        # Basic validation
        if not project_root or not name_prefix or not extension:
            raise ValueError("project_root, name_prefix and extension are required")
        if not 1 <= slot_index <= 999:
            raise ValueError("slot_index must be 1-999")
        if image_index < 1:
            raise ValueError("image_index must be ≥1")

        # Sanitize name_prefix
        safe_prefix = "".join(
            c for c in name_prefix if c.isalnum() or c in " _-"
        ).strip()
        if not safe_prefix:
            safe_prefix = "Image"

        # Extension handling (bulletproof)
        extension = extension.strip()
        if not extension.startswith("."):
            extension = "." + extension
        if "." in extension[1:]:
            extension = "." + extension.split(".", 1)[-1]
        if len(extension) < 2:
            extension = ".png"

        # Build filename
        slot_part = f"{slot_index:02d}"
        counter_part = f"{image_index:05d}"
        filename = f"{safe_prefix}{slot_part}__{counter_part}_{extension}"

        full_path = Path(project_root) / filename
        return (str(full_path).replace("\\", "/"),)


class EG_AppendSubfolder:
    """Add any extra subfolder (keeps trailing slash)."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "base_path": ("STRING", {}),
                "subfolder": ("STRING", {"default": "upscales", "multiline": False}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("path",)
    FUNCTION = "append"
    CATEGORY = "EG Tools/Paths"

    def append(self, base_path: str, subfolder: str) -> Tuple[str]:
        if not base_path or not subfolder:
            raise ValueError("Both inputs required")
        subfolder = "".join(c for c in subfolder if c.isalnum() or c in " _-/").strip()
        if not subfolder:
            subfolder = "extra"
        path = Path(base_path) / subfolder / ""
        return (str(path).replace("\\", "/"),)


class EG_PathParts:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"path": ("STRING", {})}}

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("directory", "filename", "stem", "extension")
    FUNCTION = "split"
    CATEGORY = "EG Tools/Paths"

    def split(self, path: str):
        if not path:
            raise ValueError("path required")
        p = Path(path)
        return (str(p.parent).replace("\\", "/"), p.name, p.stem, p.suffix)


class EG_WithNewExtension:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "path": ("STRING", {}),
                "extension": ("STRING", {"default": ".txt", "multiline": False}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("filepath",)
    FUNCTION = "change"
    CATEGORY = "EG Tools/Paths"

    def change(self, path: str, extension: str):
        if not path or not extension:
            raise ValueError("Both inputs required")
        if not extension.startswith("."):
            extension = "." + extension
        return (str(Path(path).with_suffix(extension)).replace("\\", "/"),)


class EG_GetDateTime:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {"format_string": ("STRING", {"default": "%Y-%m-%d_%H%M%S"})}
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("datetime_string",)
    FUNCTION = "get"
    CATEGORY = "EG Tools/Paths"

    def get(self, format_string: str):
        return (datetime.now().strftime(format_string),)


class EG_PathExists:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"path": ("STRING", {})}}

    RETURN_TYPES = ("BOOLEAN", "BOOLEAN")
    RETURN_NAMES = ("exists", "does_not_exist")
    FUNCTION = "check"
    CATEGORY = "EG Tools/Paths"

    def check(self, path: str):
        exists = Path(path).exists()
        return (exists, not exists)


class EG_ListFiles:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "directory": ("STRING", {"default": "output"}),
                "file_extension": ("STRING", {"default": ".png"}),
                "sort_by": (["alphabetical", "creation_time", "modification_time"],),
                "sort_order": (["ascending", "descending"],),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("file_list",)
    FUNCTION = "list_files"
    CATEGORY = "EG Tools/Paths"

    def list_files(
        self, directory: str, file_extension: str, sort_by: str, sort_order: str
    ):

        if not directory or not file_extension:
            return ("",)
        if not file_extension.startswith("."):
            file_extension = "." + file_extension
        p = Path(directory)
        base_path = None
        if p.is_absolute() and p.is_dir():
            base_path = p
        else:
            try:
                out = Path(folder_paths.get_output_directory()) / p
                inp = Path(folder_paths.get_input_directory()) / p
                base_path = out if out.is_dir() else inp if inp.is_dir() else None
            except:
                pass
        if not base_path:
            return ("",)
        files = [f for f in base_path.glob(f"*{file_extension}") if f.is_file()]
        reverse = sort_order == "descending"
        if sort_by == "creation_time":
            files.sort(key=lambda f: f.stat().st_ctime, reverse=reverse)
        elif sort_by == "modification_time":
            files.sort(key=lambda f: f.stat().st_mtime, reverse=reverse)
        else:
            files.sort(reverse=reverse)
        return ("\n".join(str(f).replace("\\", "/") for f in files),)


# Bonus god-tier node
class EG_IncrementCounter:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"current": ("INT", {"default": 1, "min": 1})}}

    RETURN_TYPES = ("INT",)
    RETURN_NAMES = ("next",)
    FUNCTION = "inc"
    CATEGORY = "EG Tools/Paths"
    DESCRIPTION = "Simple +1 counter — perfect for feeding back into Full Filename node"

    def inc(self, current: int):
        return (current + 1,)


# ──────────────────────────────
# MAPPINGS
# ──────────────────────────────

NODE_CLASS_MAPPINGS = {
    "EG_ProjectRoot": EG_ProjectRoot,
    "EG_PathIndexPrefix": EG_PathIndexPrefix,
    "EG_PathIndexFilename": EG_PathIndexFilename,
    "EG_AppendSubfolder": EG_AppendSubfolder,
    "EG_PathParts": EG_PathParts,
    "EG_WithNewExtension": EG_WithNewExtension,
    "EG_GetDateTime": EG_GetDateTime,
    "EG_PathExists": EG_PathExists,
    "EG_ListFiles": EG_ListFiles,
    "EG_IncrementCounter": EG_IncrementCounter,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "EG_ProjectRoot": "Project: Set Root Folder",
    "EG_PathIndexPrefix": "Project: Build Prefix (Slot Only)",
    "EG_PathIndexFilename": "Project: Full Filename (Slot + Counter)",
    "EG_AppendSubfolder": "Project: Add Subfolder",
    "EG_PathParts": "Project: Split Path",
    "EG_WithNewExtension": "Project: Change Extension",
    "EG_GetDateTime": "Project: Date/Time String",
    "EG_PathExists": "Project: Exists?",
    "EG_ListFiles": "Project: List Files",
    "EG_IncrementCounter": "Project: Increment Counter",
}
