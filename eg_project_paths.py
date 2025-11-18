import os
from pathlib import Path
from datetime import datetime
from typing import Tuple, Optional, List
import folder_paths


class EG_ProjectRoot:
    """
    Build a reusable project root path with validation.

    I created this to solve a common problem in my workflows - needing a consistent
    project structure across multiple saves and loads. This makes it easy to keep
    all related files organized.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "base_folder": (
                    "STRING",
                    {
                        "default": "MyProjects",
                        "multiline": False,
                        "tooltip": "Name of the Root/Base folder",
                    },
                ),
                "project_name": (
                    "STRING",
                    {
                        "default": "Project_1",
                        "multiline": False,
                        "tooltip": "Name of the project folder",
                    },
                ),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("project_root",)
    FUNCTION = "get_root"
    CATEGORY = "EG Tools/Paths"
    DESCRIPTION = (
        "Builds a reusable project root/base path.\n"
        "Example: base_folder='MyProjects', project_name='Project_1' -> 'MyProjects/Project_1/'.\n"
        "You can use this in save and load nodes or other useful folder requirements.\n"
    )

    def get_root(self, project_name: str, base_folder: str) -> Tuple[str]:
        # Input validation - I'm being strict here because path issues can be hard to debug
        if not project_name or not isinstance(project_name, str):
            raise ValueError("project_name must be a non-empty string")

        if not base_folder or not isinstance(base_folder, str):
            raise ValueError("base_folder must be a non-empty string")

        # Sanitize project name - removing weird characters that could cause issues
        project_name = "".join(
            c for c in project_name if c.isalnum() or c in (" ", "-", "_")
        ).rstrip()

        if not project_name:
            raise ValueError("project_name contains no valid characters")

        # Build the path and make sure it uses forward slashes (better for cross-platform)
        path = Path(base_folder) / project_name / ""
        return (str(path).replace("\\", "/"),)


class EG_PathIndexPrefix:
    """
    Build a slot-based filename prefix for Save nodes.

    This makes it easy to organize different types of outputs within a project.
    I use this to separate frames, intermediate results, and final renders.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "project_root": ("STRING", {}),
                "slot_index": ("INT", {"default": 1, "min": 1, "max": 999, "step": 1}),
                "name_prefix": ("STRING", {"default": "Image", "multiline": False}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("filename_prefix",)
    FUNCTION = "get_prefix"
    CATEGORY = "EG Tools/Paths"
    DESCRIPTION = (
        "Builds a slot-based filename prefix for saving images or text.\n"
        "Example: project_root='MyProjects/Project_1', slot_index=1, name_prefix='Image' "
        "-> 'MyProjects/Project_1/Image01_'."
    )

    def get_prefix(
        self, project_root: str, slot_index: int, name_prefix: str
    ) -> Tuple[str]:
        # Validate inputs
        if not project_root or not isinstance(project_root, str):
            raise ValueError("project_root must be a non-empty string")

        if not isinstance(slot_index, int) or slot_index < 1 or slot_index > 999:
            raise ValueError("slot_index must be an integer between 1 and 999")

        if not name_prefix or not isinstance(name_prefix, str):
            raise ValueError("name_prefix must be a non-empty string")

        # Sanitize name_prefix
        name_prefix = "".join(
            c for c in name_prefix if c.isalnum() or c in (" ", "-", "_")
        ).rstrip()

        if not name_prefix:
            raise ValueError("name_prefix contains no valid characters")
        # Format with leading zeros for proper sorting in file explorers
        slot_str = f"{slot_index:02d}"
        prefix = Path(project_root) / f"{name_prefix}{slot_str}_"
        return (str(prefix).replace("\\", "/"),)


class EG_PathIndexFilename:
    """
    Build a full filepath matching ComfyUI's Save pattern.

    I designed this to match ComfyUI's naming convention exactly, making it
    compatible with existing workflows while adding more flexibility.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "project_root": ("STRING", {}),
                "slot_index": ("INT", {"default": 1, "min": 1, "max": 999, "step": 1}),
                "name_prefix": ("STRING", {"default": "Image", "multiline": False}),
                "image_index": (
                    "INT",
                    {"default": 1, "min": 1, "max": 99999, "step": 1},
                ),
                "extension": ("STRING", {"default": ".png", "multiline": False}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("filepath",)
    FUNCTION = "get_filename"
    CATEGORY = "EG Tools/Paths"
    DESCRIPTION = (
        "Builds a full filepath matching ComfyUI's Save pattern.\n"
        "Example: project_root='MyProjects/Project_1', slot_index=1, "
        "name_prefix='Image', image_index=1, extension='.png' "
        "-> 'MyProjects/Project_1/Image01__00001_.png'."
    )

    def get_filename(
        self,
        project_root: str,
        slot_index: int,
        name_prefix: str,
        image_index: int,
        extension: str,
    ) -> Tuple[str]:
        # Validate inputs
        if not project_root or not isinstance(project_root, str):
            raise ValueError("project_root must be a non-empty string")

        if not isinstance(slot_index, int) or slot_index < 1 or slot_index > 999:
            raise ValueError("slot_index must be an integer between 1 and 999")

        if not name_prefix or not isinstance(name_prefix, str):
            raise ValueError("name_prefix must be a non-empty string")

        if not isinstance(image_index, int) or image_index < 1 or image_index > 99999:
            raise ValueError("image_index must be an integer between 1 and 99999")

        if not extension or not isinstance(extension, str):
            raise ValueError("extension must be a non-empty string")

        # Sanitize extension - make sure it starts with a dot
        if not extension.startswith("."):
            extension = "." + extension

        # Validate extension format
        if len(extension) < 2 or extension[1] != ".":
            raise ValueError("extension must be a valid file extension (e.g., '.png')")

        # Sanitize name_prefix
        name_prefix = "".join(
            c for c in name_prefix if c.isalnum() or c in (" ", "-", "_")
        ).rstrip()

        if not name_prefix:
            raise ValueError("name_prefix contains no valid characters")

        slot_str = f"{slot_index:02d}"
        filename_str = f"{name_prefix}{slot_str}__{image_index:05d}_{extension}"

        path = Path(project_root) / filename_str
        return (str(path).replace("\\", "/"),)


class EG_AppendSubfolder:
    """
    Append a subfolder to a base path with trailing slash.

    This is useful for organizing different types of assets within a project.
    I use it to create subfolders for frames, masks, references, etc.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "base_path": ("STRING", {}),
                "subfolder": ("STRING", {"default": "Subfolder", "multiline": False}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("path",)
    FUNCTION = "append_subfolder"
    CATEGORY = "EG Tools/Paths"
    DESCRIPTION = (
        "Appends a subfolder to a base path and ensures a trailing slash.\n"
        "Example: base_path='MyProjects/Project_1', subfolder='Frames' "
        "-> 'MyProjects/Project_1/Frames/'."
    )

    def append_subfolder(self, base_path: str, subfolder: str) -> Tuple[str]:
        # Validate inputs
        if not base_path or not isinstance(base_path, str):
            raise ValueError("base_path must be a non-empty string")

        if not subfolder or not isinstance(subfolder, str):
            raise ValueError("subfolder must be a non-empty string")

        # Sanitize subfolder
        subfolder = "".join(
            c for c in subfolder if c.isalnum() or c in (" ", "-", "_", "/")
        ).rstrip()

        if not subfolder:
            raise ValueError("subfolder contains no valid characters")

        path = Path(base_path) / subfolder / ""
        return (str(path).replace("\\", "/"),)


class EG_PathParts:
    """
    Split a path into directory, filename, stem, and extension.

    I added this because sometimes I need to extract just the filename or
    directory from a full path for use in other nodes.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"path": ("STRING", {})}}

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("directory", "filename", "stem", "extension")
    FUNCTION = "split"
    CATEGORY = "EG Tools/Paths"
    DESCRIPTION = (
        "Splits a path string into directory, filename, stem, and extension.\n"
        "Useful for reusing parts of an existing path."
    )

    def split(self, path: str) -> Tuple[str, str, str, str]:
        # Validate input
        if not path or not isinstance(path, str):
            raise ValueError("path must be a non-empty string")

        p = Path(path)
        directory = str(p.parent).replace("\\", "/")
        filename = p.name
        stem = p.stem
        extension = p.suffix
        return (directory, filename, stem, extension)


class EG_WithNewExtension:
    """
    Replace the extension on a given path.

    This is handy when you want to save the same base filename with different
    formats, like saving a .png preview and a .jpg thumbnail.
    """

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
    FUNCTION = "with_extension"
    CATEGORY = "EG Tools/Paths"
    DESCRIPTION = (
        "Replaces the extension on a path. If the extension does not start with '.', "
        "it will be added automatically."
    )

    def with_extension(self, path: str, extension: str) -> Tuple[str]:
        # Validate inputs
        if not path or not isinstance(path, str):
            raise ValueError("path must be a non-empty string")

        if not extension or not isinstance(extension, str):
            raise ValueError("extension must be a non-empty string")

        # Sanitize extension
        if not extension.startswith("."):
            extension = "." + extension

        # Validate extension format
        if len(extension) < 2:
            raise ValueError("extension must be a valid file extension (e.g., '.txt')")

        p = Path(path)
        new_path = p.with_suffix(extension)
        return (str(new_path).replace("\\", "/"),)


class EG_GetDateTime:
    """
    Generates a formatted date/time string.

    I find this useful for creating unique filenames or timestamps in my workflows.
    The default format is designed to be sortable in file explorers.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "format_string": ("STRING", {"default": "%Y-%m-%d_%H%M%S"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("datetime_string",)
    FUNCTION = "get_datetime"
    CATEGORY = "EG Tools/Paths"
    DESCRIPTION = (
        "Generates a formatted date/time string, perfect for unique filenames."
    )

    def get_datetime(self, format_string: str) -> Tuple[str]:
        # Validate input
        if not format_string or not isinstance(format_string, str):
            raise ValueError("format_string must be a non-empty string")

        try:
            dt_str = datetime.now().strftime(format_string)
            return (dt_str,)
        except ValueError as e:
            raise ValueError(f"Invalid format string: {e}")


class EG_PathExists:
    """
    Checks if a file or directory exists at the given path.

    This is useful for conditional logic in workflows, like only proceeding
    if a required file exists.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"path": ("STRING", {})}}

    RETURN_TYPES = ("BOOLEAN", "BOOLEAN")
    RETURN_NAMES = ("exists", "does_not_exist")
    FUNCTION = "check_exists"
    CATEGORY = "EG Tools/Paths"
    DESCRIPTION = (
        "Checks if a file or directory exists. Outputs two booleans for routing."
    )

    def check_exists(self, path: str) -> Tuple[bool, bool]:
        # Validate input
        if not path or not isinstance(path, str):
            raise ValueError("path must be a non-empty string")

        p = Path(path)
        exists = p.exists()
        return (exists, not exists)


class EG_ListFiles:
    """
    Lists files in a directory with filtering and sorting.

    I added this to make it easier to work with existing files in a directory,
    like loading all images in a folder for batch processing.
    """

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
    DESCRIPTION = "Lists files in a directory, with filtering and sorting."

    def list_files(
        self, directory: str, file_extension: str, sort_by: str, sort_order: str
    ) -> Tuple[str]:
        # Validate inputs
        if not directory or not isinstance(directory, str):
            raise ValueError("directory must be a non-empty string")

        if not file_extension or not isinstance(file_extension, str):
            raise ValueError("file_extension must be a non-empty string")

        if sort_by not in ["alphabetical", "creation_time", "modification_time"]:
            raise ValueError(
                "sort_by must be one of: alphabetical, creation_time, modification_time"
            )

        if sort_order not in ["ascending", "descending"]:
            raise ValueError("sort_order must be either 'ascending' or 'descending'")

        # Sanitize extension
        if not file_extension.startswith("."):
            file_extension = "." + file_extension

        p = Path(directory)
        base_path = None

        # Check if the provided path is absolute and exists
        if p.is_absolute():
            if p.is_dir():
                base_path = p
        else:
            # If relative, check against ComfyUI's output and then input directories
            try:
                output_dir = Path(folder_paths.get_output_directory())
                input_dir = Path(folder_paths.get_input_directory())

                path_in_output = output_dir / p
                path_in_input = input_dir / p

                if path_in_output.is_dir():
                    base_path = path_in_output
                elif path_in_input.is_dir():
                    base_path = path_in_input
            except Exception as e:
                print(
                    f"WARNING: [EG_ListFiles] Could not determine ComfyUI directories: {e}"
                )

        # If we couldn't find a valid directory, return empty
        if base_path is None:
            print(f"WARNING: [EG_ListFiles] Directory not found: '{directory}'")
            return ("",)

        try:
            # Use glob to find all files with the specified extension
            files = list(base_path.glob(f"*{file_extension}"))

            # Filter out directories (glob might include them in some cases)
            files = [f for f in files if f.is_file()]

            # Sort the list of files
            reverse_order = sort_order == "descending"
            if sort_by == "creation_time":
                files.sort(key=lambda f: f.stat().st_ctime, reverse=reverse_order)
            elif sort_by == "modification_time":
                files.sort(key=lambda f: f.stat().st_mtime, reverse=reverse_order)
            else:  # alphabetical
                files.sort(reverse=reverse_order)

            # Join the file paths into a single string, one per line
            file_list_str = "\n".join([str(f).replace("\\", "/") for f in files])
            return (file_list_str,)

        except Exception as e:
            print(f"ERROR: [EG_ListFiles] Failed to list files: {e}")
            return ("",)


# --- MAPPINGS ---
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
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "EG_ProjectRoot": "Path: Project Root",
    "EG_PathIndexPrefix": "Path: Index Prefix",
    "EG_PathIndexFilename": "Path: Index Filename",
    "EG_AppendSubfolder": "Path: Append Subfolder",
    "EG_PathParts": "Path: Split Parts",
    "EG_WithNewExtension": "Path: With New Extension",
    "EG_GetDateTime": "Path: Get Date Time String",
    "EG_PathExists": "Path: Exists?",
    "EG_ListFiles": "Path: List Files in Directory",
}
