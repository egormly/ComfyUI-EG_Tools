# eg_image_info.py

import torch
import torch.nn.functional as F
from typing import Tuple, Union


class EG_ImageInfo:
    """
    Utility node for image information and Qwen preparation.

    I created this to solve a common problem in my workflows - needing to know image dimensions
    while also having the option to resize images for vision models like Qwen. This node handles
    both tasks efficiently.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "mode": (
                    ["Info only", "Qwen Prep"],
                    {"default": "Info only", "tooltip": "Select processing mode"},
                ),
                "qwen_max_pixels": (
                    "INT",
                    {
                        "default": 1_000_000,
                        "min": 262_144,  # 512 * 512
                        "max": 8_388_608,  # 4096*2048 (increased from 4M)
                        "step": 65_536,
                        "tooltip": "Maximum pixels after resizing (Qwen mode only)",
                    },
                ),
                "qwen_multiple_of": (
                    "INT",
                    {
                        "default": 16,
                        "min": 1,
                        "max": 256,  # Increased for flexibility
                        "step": 1,
                        "tooltip": "Round dimensions to multiple of this value (Qwen mode only)",
                    },
                ),
            }
        }

    RETURN_TYPES = ("IMAGE", "INT", "INT")
    RETURN_NAMES = ("image", "width", "height")
    FUNCTION = "process"
    CATEGORY = "EG Tools/Image"
    OUTPUT_NODE = False
    DESCRIPTION = (
        "Features:\n"
        "- Outputs image dimensions (width, height) - info only\n"
        "\n"
        "- Qwen Prep\n"
        "   * Optional Qwen preparation mode that:\n"
        "   * Preserves aspect ratio\n"
        "   * Limits total pixels (default ~1MP)\n"
        "   * Rounds dimensions to multiples of N (default 16)\n"
        "   * Uses bicubic interpolation for high-quality resizing\n"
        "\n"
        "Input:\n"
        "- IMAGE: A tensor of shape [B, H, W, C] with values in [0, 1]\n"
        "\n"
        "Output:\n"
        "- IMAGE: The original or processed image\n"
        "- INT: Width in pixels\n"
        "- INT: Height in pixels\n"
    )

    def process(
        self,
        image: torch.Tensor,
        mode: str,
        qwen_max_pixels: int,
        qwen_multiple_of: int,
    ) -> Tuple[torch.Tensor, int, int]:
        """
        Process the image based on the selected mode.

        Args:
            image: Input tensor of shape [B, H, W, C]
            mode: Processing mode ("Info only" or "Qwen Prep")
            qwen_max_pixels: Maximum pixels for Qwen mode
            qwen_multiple_of: Multiple to round dimensions to

        Returns:
            Tuple of (processed_image, width, height)
        """
        # Input validation - I'm being strict here because ComfyUI can be picky
        if not isinstance(image, torch.Tensor):
            raise ValueError("Input must be a torch.Tensor")

        if image.dim() != 4:
            raise ValueError(f"Expected 4D tensor [B,H,W,C], got {image.dim()}D")

        if image.size(0) == 0:
            raise ValueError("Batch size cannot be zero")

        # Make sure values are in valid range [0, 1]
        image = torch.clamp(image, 0.0, 1.0)

        # Get original dimensions
        b, h, w, c = image.shape

        # Validate parameters with reasonable bounds
        qwen_max_pixels = max(262_144, min(8_388_608, int(qwen_max_pixels)))
        qwen_multiple_of = max(1, min(256, int(qwen_multiple_of)))

        if mode == "Qwen Prep":
            # Calculate target dimensions for Qwen
            target_w, target_h = self._calculate_qwen_dimensions(
                w, h, qwen_max_pixels, qwen_multiple_of
            )

            # Only resize if dimensions actually changed
            if target_w != w or target_h != h:
                image = self._resize_image(image, target_h, target_w)
                w, h = target_w, target_h

        return (image, int(w), int(h))

    def _calculate_qwen_dimensions(
        self, w: int, h: int, max_pixels: int, multiple_of: int
    ) -> Tuple[int, int]:
        """
        Calculate target dimensions for Qwen preparation.

        This method ensures the image fits within the pixel limit while maintaining
        aspect ratio and rounding to the required multiple.
        """
        # Calculate scaling if needed
        orig_area = w * h
        if orig_area > max_pixels:
            # Calculate scale factor to fit within max_pixels
            scale = (max_pixels / float(orig_area)) ** 0.5
            target_w = int(round(w * scale))
            target_h = int(round(h * scale))
        else:
            target_w, target_h = w, h

        # Round to nearest multiple - this is important for some vision models
        def round_to_multiple(v: int, mult: int) -> int:
            """Round value to nearest multiple of mult."""
            return max(mult, int(round(v / mult)) * mult)

        target_w = round_to_multiple(target_w, multiple_of)
        target_h = round_to_multiple(target_h, multiple_of)

        # Ensure minimum dimensions
        target_w = max(16, target_w)
        target_h = max(16, target_h)

        return target_w, target_h

    def _resize_image(
        self, image: torch.Tensor, target_h: int, target_w: int
    ) -> torch.Tensor:
        """
        Resize image using bicubic interpolation.

        I chose bicubic because it provides good quality for most image types
        without being too computationally expensive.
        """
        # Permute to [B, C, H, W] for interpolation
        img_ch_first = image.permute(0, 3, 1, 2)

        # Perform bicubic interpolation
        resized = F.interpolate(
            img_ch_first,
            size=(target_h, target_w),
            mode="bicubic",
            align_corners=False,
            antialias=True,  # Added for better quality
        )

        # Permute back to [B, H, W, C] and clamp values
        return resized.permute(0, 2, 3, 1).clamp(0.0, 1.0)


# Register the node with ComfyUI
NODE_CLASS_MAPPINGS = {
    "EG_ImageInfo": EG_ImageInfo,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "EG_ImageInfo": "Image Info / Qwen Prep",
}
