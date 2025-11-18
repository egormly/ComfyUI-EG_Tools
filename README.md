# ComfyUI-EG_Tools
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![ComfyUI](https://img.shields.io/badge/ComfyUI-Custom%20Node-blue)](https://github.com/comfyanonymous/ComfyUI)

Quality-of-life utility nodes for ComfyUI.

The goal of this pack is to provide basic utility tools. This pack may grow over time as I see the need for basic nodes ComfUI does not provide. This pack does not rewuire complex installation nor external packages. It is drop and go.

Currently included:

Smart switching - Multiple type switches allowing one or more data connections with selectable or default output.

Image information and preperation (for Qwen Edit etc) - Bsic information of an image and preperation for proper pixels for Qwen Edit.

Path Helpers -  Simple path settiing, removing repetitive, error-prone wiring from complex workflows (like multi-step image and video pipelines) by centralizing things such as project paths and prefixes into simple, reusable nodes. This is particularly useful for hardcoding path in repetitive workflows.

---

## Features

### Path Helpers
**Category:** `EG Tools/Paths`

These nodes are designed to make file naming and project structuring consistent across large workflows.

- **Project Root**
  Build a reusable project root string from a base folder and project name.
  - Example: `base_folder="Projects"`, `project_name="Project_1"` → `MyProject/Project_1/`

- **Path Index Prefix**
  Build a slot-based filename prefix that plugs directly into a `Save` node’s `filename_prefix` input.
  - Example: `project_root="MyProject/Project_1/"`, `slot_index=1`, `name_prefix="Image"`
  - → `MyProject/Project_1/Image01_`

- **Path Index Filename**
  Build the full filename string that matches ComfyUI’s `Save Image` / `Save Text` naming pattern.
  - Example: `project_root="MyProject/Project_1/"`, `slot_index=1`, `name_prefix="Image"`, `image_index=1`, `extension=".png"`
  - → `MyProject/Project_1/Image01__00001_.png`

### Smart Switches
**Category:** `EG Tools/Switches`

These nodes make it easy to route data dynamically in a graph without rewiring cables every time you change your mind.

All **Smart Switch** nodes share the same behavior:

- `force_input_index = 0` → **auto mode**
  Returns the *first* connected input that has data (`input_1`, then `input_2`, etc.)
- `force_input_index > 0` → **manual mode**
  Forces a specific input index (1..N), as long as that input is connected and not `None`.

If no valid input is found, they output `None` (or `""` for text, to avoid type issues).

#### Smart Switch nodes
Each node accepts several inputs of the given type (`input_1` … `input_N`) and returns one:

- **Smart Switch (Image)**
  - **Type:** `IMAGE`
  - Route between multiple image sources (different pipelines, models, or styles) from a single control point.

- **Smart Switch (Latent)**
  - **Type:** `LATENT`
  - Switch between different latent branches (e.g. different encoders, different noising branches).

- **Smart Switch (CLIP)**
  - **Type:** `CLIP`
  - Choose between multiple CLIP encoders or prompt encodings.

- **Smart Switch (Conditioning)**
  - **Type:** `CONDITIONING`
  - Route different positive/negative conditioning setups through one output.

- **Smart Switch (Model)**
  - **Type:** `MODEL`
  - Switch between different models from a single control (e.g. base vs finetune, different styles).

- **Smart Switch (VAE)**
  - **Type:** `VAE`
  - Choose between multiple VAEs (standard, anime, photographic, etc.).

- **Smart Switch (Float)**
  - **Type:** `FLOAT`
  - Switch between numeric values (e.g. strength, CFG, noise, blending factors).

- **Smart Switch (Int)**
  - **Type:** `INT`
  - Choose between integer settings (e.g. frame indices, step counts, seed offsets).

- **Smart Switch (Text)**
  - **Type:** `STRING`
  - Route between different text inputs (prompts, tags, labels). If nothing is selected, outputs an empty string `""`.


These switches are designed to be dropped into existing graphs with minimal friction, so you can experiment with alternate branches, models, and values without constantly rewiring your workflow.


### Image Utilities
**Category:** `EG Tools/Image`

- **Image Info / Qwen Prep**
  A dual-purpose utility node that can either output an image's dimensions or prepare it for use with vision models like Qwen-VL.

  The node's behavior is controlled by the `mode` dropdown:

  - **Info only**
    - Simply outputs the original image's width and height without any modification.
    - The `image` output is a direct copy of the input.

  - **Qwen Prep**
    - Resizes the image to be compatible with vision models, optimizing for token count while preserving quality.
    - **Features:**
      - Preserves the original aspect ratio.
      - Resizes to fit within a maximum pixel count (default ~1MP).
      - Rounds dimensions to a multiple of a specified number (default 16).
      - Uses high-quality bicubic interpolation.

  **Inputs:**
  - `image`: The input image tensor.
  - `mode`: Selects between `"Info only"` and `"Qwen Prep"`.
  - `qwen_max_pixels`: The maximum total pixels for the resized image (Qwen mode only).
  - `qwen_multiple_of`: Rounds width and height to be a multiple of this value (Qwen mode only).

  **Outputs:**
  - `image`: The original image (Info mode) or the processed image (Qwen mode).
  - `width`: The final width of the output image in pixels.
  - `height`: The final height of the output image in pixels.

  ## Node Showcase

Here is a visual look at the nodes included in EG_Tools.

### Path Tools

This collection of nodes (`EG Tools/Paths`) helps you build consistent and reusable file paths for your projects, eliminating manual string construction and reducing errors.

![Path Tools Node Collection](/images/path_tools.png)

### Image Info / Qwen Prep

A look at the `EG Tools/Image` node's interface. You can see the inputs, outputs, and the parameters that control its two modes: simple dimension reporting and advanced image preparation for vision models.

![Image Info Node Interface](/images/qwen_info.png)


### Smart Switches in Action

The `Smart Switch` nodes allow you to dynamically select from multiple inputs. This image shows an `INT` switch where `input_3` is currently the active output, demonstrating how you can route different values or data types through a single node.

![Smart Switch Selection](/images/smart_switches.png)

### Samples of the Smart Switch Family

For your convenience, EG_Tools provides a `Smart Switch` for every major data type in ComfyUI. This allows you to route images, models, prompts, and more without having to rewire your entire workflow.

![Smart Switch Node Collection](/images/smart_switches2.png)

---

## Installation

From your ComfyUI `custom_nodes` directory:

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/egormly/ComfyUI-EG_Tools.git