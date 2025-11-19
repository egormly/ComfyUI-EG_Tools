import os
import io
import glob
import hashlib
from typing import List
from PIL import Image
import numpy as np

try:
    import torch

    TORCH_OK = True
except Exception:
    TORCH_OK = False

from aiohttp import web

# Comfy internals
try:
    from server import PromptServer
except Exception:
    PromptServer = None

NODE_NAME = "Visual Image Loader"
NODE_CATEGORY = "EG Tools/Image"

# ---- Simple in-process thumbnail cache (key -> (mtime, size, thumb_bytes)) ----
# key = f"{path}|{max_size}"
_THUMB_CACHE = {}  # { key: (mtime, size, bytes) }


def _thumb_key(path: str, max_size: int) -> str:
    return f"{path}|{max_size}"


def _make_thumb(path: str, max_size=256) -> bytes:
    """
    Generate a small **square** PNG thumbnail (center-cropped) and return bytes.
    Cached by (path, mtime, size).
    """
    try:
        st = os.stat(path)
        mtime = st.st_mtime
    except Exception:
        return b""

    k = _thumb_key(path, max_size)
    cached = _THUMB_CACHE.get(k)
    if cached and cached[0] == mtime and cached[1] == max_size:
        return cached[2]

    try:
        with Image.open(path) as im:
            im = im.convert("RGB")

            # ---- center-crop to square before resizing (COVER behavior) ----
            w, h = im.size
            if w != h:
                side = min(w, h)
                left = (w - side) // 2
                top = (h - side) // 2
                im = im.crop((left, top, left + side, top + side))

            resample = getattr(Image, "Resampling", Image).LANCZOS
            im = im.resize((max_size, max_size), resample)

            buf = io.BytesIO()
            im.save(buf, format="PNG", optimize=True)
            data = buf.getvalue()
            _THUMB_CACHE[k] = (mtime, max_size, data)
            return data
    except Exception:
        return b""


def _to_batched_tensor(im: Image.Image):
    """
    PIL -> torch.FloatTensor in [0,1] with shape (1, H, W, 3).
    This is what ComfyUI expects for IMAGE.
    """
    arr = np.array(im)
    if arr.ndim == 2:
        arr = np.stack([arr, arr, arr], axis=-1)
    elif arr.shape[2] == 4:
        arr = arr[:, :, :3]

    arr = arr.astype(np.float32) / 255.0  # H W C
    if TORCH_OK:
        t = torch.from_numpy(arr).contiguous()  # H W C
        t = t.unsqueeze(0)  # 1 H W C  (batch=1)
        return t
    else:
        # Fallback to numpy with a fake batch dimension if torch missing
        return arr[np.newaxis, ...]  # (1, H, W, 3)


def _list_images(folder: str, pattern: str, sort: str) -> List[str]:
    if not folder or not os.path.isdir(folder):
        return []
    patterns = [p.strip() for p in pattern.replace(",", ";").split(";") if p.strip()]
    if not patterns:
        patterns = ["*.png", "*.jpg", "*.jpeg", "*.webp", "*.bmp"]
    paths = []
    for pat in patterns:
        paths.extend(glob.glob(os.path.join(folder, pat)))
    seen = set()
    uniq = []
    for p in paths:
        if p not in seen:
            seen.add(p)
            uniq.append(p)
    if sort == "Name ↑":
        uniq.sort(key=lambda p: os.path.basename(p).lower())
    elif sort == "Name ↓":
        uniq.sort(key=lambda p: os.path.basename(p).lower(), reverse=True)
    elif sort == "Date ↑":
        uniq.sort(key=lambda p: os.path.getmtime(p))
    else:  # Date ↓ (default)
        uniq.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    return uniq


# ------------------ REST endpoints for the front-end panel ------------------


async def ep_list(request: web.Request):
    """GET /image_folder_picker/list?folder=...&pattern=...&sort=...&limit=..."""
    folder = request.rel_url.query.get("folder", "")
    pattern = request.rel_url.query.get("pattern", "*.png;*.jpg;*.jpeg;*.webp;*.bmp")
    sort = request.rel_url.query.get("sort", "Date ↓")
    try:
        limit = int(request.rel_url.query.get("limit", "256"))
    except Exception:
        limit = 256

    files = _list_images(folder, pattern, sort)[:limit]
    data = [{"name": os.path.basename(p), "path": p} for p in files]
    return web.json_response({"ok": True, "files": data})


async def ep_thumb(request: web.Request):
    """GET /image_folder_picker/thumb?path=...&size=..."""
    path = request.rel_url.query.get("path", "")
    try:
        size = int(request.rel_url.query.get("size", "256"))
    except Exception:
        size = 256
    size = max(64, min(size, 1024))  # clamp

    if not path or not os.path.isfile(path):
        return web.Response(status=404)

    png = _make_thumb(path, max_size=size)
    if not png:
        return web.Response(status=404)
    return web.Response(body=png, content_type="image/png")


def _register_endpoints():
    """
    Works across ComfyUI versions where PromptServer.instance.routes is an aiohttp.RouteTableDef.
    """
    if PromptServer is None or not hasattr(PromptServer, "instance"):
        print(
            "[ImageFolderPicker] PromptServer not available; endpoints not registered."
        )
        return
    routes = PromptServer.instance.routes
    try:
        routes.get("/visual_image_loader/list")(ep_list)
        routes.get("/visual_image_loader/thumb")(ep_thumb)
        print("[visual_image_loader] endpoints registered (RouteTableDef.get)")
    except Exception as e:
        print(f"[visual_image_loader] endpoint registration failed: {e}")


# ----------------------------- The Node class -------------------------------


class ImageFolderPicker:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "folder": ("STRING", {"default": "", "multiline": False}),
                "pattern": ("STRING", {"default": "*.png;*.jpg;*.jpeg;*.webp;*.bmp"}),
                "sort": (["Date ↓", "Date ↑", "Name ↓", "Name ↑"],),
                "selected": ("STRING", {"default": "", "multiline": False}),
                "max_thumbs": (
                    "INT",
                    {"default": 256, "min": 16, "max": 2048, "step": 1},
                ),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "load"
    CATEGORY = NODE_CATEGORY
    OUTPUT_NODE = False

    def load(
        self,
        folder: str,
        pattern: str,
        sort: str,
        selected: str,
        max_thumbs: int,
        unique_id=None,
    ):
        """
        Load currently selected image. Front-end sets 'selected' to a file path.
        Returns a torch tensor of shape (1, H, W, 3), float32 in [0,1].
        """
        path = selected.strip()
        if not path:
            files = _list_images(folder, pattern, sort)
            if files:
                path = files[0]
            else:
                # Tiny black fallback: (1, 8, 8, 3)
                if TORCH_OK:
                    img = torch.zeros((1, 8, 8, 3), dtype=torch.float32)
                    return (img,)
                else:
                    arr = np.zeros((1, 8, 8, 3), dtype=np.float32)
                    return (arr,)

        try:
            with Image.open(path) as im:
                im = im.convert("RGB")
                return (_to_batched_tensor(im),)
        except Exception:
            # Fallback tiny black
            if TORCH_OK:
                img = torch.zeros((1, 8, 8, 3), dtype=torch.float32)
                return (img,)
            else:
                arr = np.zeros((1, 8, 8, 3), dtype=np.float32)
                return (arr,)

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        """
        Re-run when selection changes or folder/pattern/sort changes.
        """
        folder = kwargs.get("folder", "")
        pattern = kwargs.get("pattern", "")
        sort = kwargs.get("sort", "")
        selected = kwargs.get("selected", "")
        max_thumbs = kwargs.get("max_thumbs", 256)
        key = f"{folder}|{pattern}|{sort}|{selected}|{max_thumbs}"
        return hashlib.md5(key.encode("utf-8")).hexdigest()


# --------------- Register node and endpoints with Comfy server --------------

NODE_CLASS_MAPPINGS = {NODE_NAME: ImageFolderPicker}
NODE_DISPLAY_NAME_MAPPINGS = {NODE_NAME: f"{NODE_NAME}"}
# The module top-level import hook runs on ComfyUI startup
_register_endpoints()
print("[visual_image_loader] node module loaded.")
