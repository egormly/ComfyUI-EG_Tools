# ComfyUI-EG_Tools
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![ComfyUI](https://img.shields.io/badge/ComfyUI-Custom%20Node-blue)](https://github.com/comfyanonymous/ComfyUI)

### Quality-of-life utility nodes for ComfyUI.

The goal of this pack is to provide basic utility tools. This pack may grow over time as I see the need for basic nodes ComfUI does not provide (or are in bloated node packs). This pack does not require complex installation nor external packages. It is drop and go.

Currently included: *(scroll down to see screenshots of the nodes in this pack)*

**Smart switching** - Multiple type switches allowing one or more data connections with selectable or default output.

**Image information and preparation** (for Qwen Edit etc) - Basic information of an image and preparation for proper pixels for Qwen Edit. 

**Image Save and Image Browse nodes** (Addvanced and special use case nodes. See below for more information)

**Path Helpers** -  Simple path setting, removing repetitive, error-prone wiring from complex workflows (like multi-step image and video pipelines) by centralizing things such as project paths and prefixes into simple, reusable nodes. This is particularly useful for hardcoding path in repetitive workflows.

**Get and Set Value nodes** - Other providers have these, but this one offers a bit more, auto title set to the Key you decide on and the information of what is being passed visually, so you can verify it.

### Example Workflow: Universal txt2img (SD1.5 ↔ any other model)

Download this file into ComfyUI → [eg_tools_example.json](workflows/eg_tools_example.json) Or check out the workflows folder

Works with only built-in nodes + EG_Tools. Try disconnecting/reconnecting the second checkpoint to see the smart switches in action! Or try the force index! You may have to select your local models - this uses base SD 1.5 and a (once) popular 1.5 model as example.

---
## Nodes included in this pack:

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


### SetValue & GetValue (virtual Set/Get teleports)

A pair of nodes that act like
named “teleports” inside your graph. They help de-spaghetti large
workflows without adding any backend complexity.

- **Category:** `EG Tools`
- **Nodes:**
  - `SetValue`
  - `GetValue`

These nodes are implemented as virtual (frontend) nodes – they do **not**
change the data sent to the backend and add no extra compute. They
only reroute connections in the UI.

### SetValue

`SetValue` lets you “name” any value and pass it on:

- **Widget – `Key`**  
  A string name (e.g. `main_model`, `ref_image`, `wan_latent`).
- **Widget – `Info` (read-only)**  
  Automatically filled with a short summary like  
  `MODEL from CheckpointLoader (flux1.1-dev.safetensors)` or  
  `IMAGE from LoadImage (my_picture.png)` when something is connected.
- **Input – `in`**  
  Generic input; automatically adopts the type of whatever you connect
  (MODEL, IMAGE, LATENT, CONDITIONING, etc.).
- **Output – `out`**  
  Same type as the input. You can wire this forward like a normal
  passthrough.

**Quality-of-life details:**

- When you set the `Key`, the node title automatically updates to  
  `Set <Key>` (e.g. `Set main_model`).  
  When the node is collapsed, you can still see what it is at a glance.
- The `Info` field lets you inspect what is flowing through the slot
  without needing a separate “show” node.

### GetValue

`GetValue` retrieves the value from any `SetValue` node with a matching
key and forwards its connection, acting like a named teleporter.

- **Widget – `Key` (combo)**  
  Dropdown listing all keys from existing `SetValue` nodes in the
  current graph.
- **Widget – `Info` (read-only)**  
  Mirrors the `Info` text from the matching `SetValue`, so you can see
  exactly what you’re pulling.
- **Output – `out`**  
  Type automatically matches the type of the connected `SetValue`
  input.

Internally, `GetValue` does **not** store a separate copy of the data.
Instead, it virtually forwards the same upstream connection feeding the
corresponding `SetValue`. From the backend’s point of view, it’s as if
you wired directly from the original source node.

### Why use SetValue / GetValue?

- **De-spaghetti large graphs**  
  Instead of dragging a MODEL or LATENT wire across the entire canvas,
  you can:

  1. Connect it once into `SetValue (Key = "main_model")`.
  2. Use `GetValue (Key = "main_model")` wherever you need it.

- **Readable even when collapsed**  
  Auto-titling (`Set main_model`, `Get main_model`) plus the `Info`
  widget makes it obvious what each pair is doing.

- **Type-agnostic**  
  Works with models, images, latents, conditioning, etc., without
  separate typed Set/Get nodes.

These nodes are especially helpful in my complex video / multi-stage and grouped
workflows where the same resources (models, reference images, latents)
need to be reused in multiple places without turning the canvas into a
pile of crossing wires. I have used other nodes available but find the auto title and visual indication of the data being passed very useful.


### Image Utilities

**Category:** `EG Tools/Image`

- **Save Image (Exact Path)**
    *   Unlike the standard ComfyUI save node, this respects your filename inputs 100%.
    *   Exact Filename Control: No forced counters (`_00001`) or double extensions (`.png.png`). If you input `MyImage.png`, it saves `MyImage.png`.
    *   Absolute Path Support: Save directly to external drives or network paths (e.g., `D:/Art/ProjectA/image.png`). Relative paths automatically default to the standard `output/` folder.
    *   Universal Preview: Solves the "blind save" issue. Even if you save to an external drive, this node generates a temporary preview so you can still see your results in ComfyUI.
    *   Auto-Format Detection: Simply change your filename extension to change the format.
    *   `.png` = Lossless + Metadata (Workflow embedding)
    *   `.jpg` / `.webp` = Optimized compression (with Quality slider)
    *  #### Careful:  This save node WILL overwrite existing files.


- **Visual Image Loader**

   *   This node allows you to set a folder and then select images based on thumbnails. Good for projects using a single reference folder with m,ultiple images.  Stays persistantly open untiol you close it. The image selected is automatically populated with a single click.


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
---
### Save Image (Exact Path )

Be careful with this save node, it is for exact pathing and for use with other folder and root nodes and will overwrite existing images. This is intended for specific workflow needs, not multiple generations through a basic save image node.

This example saves to ComfyUI\output\MyImages\Image.png

![Save Image](/images/saveimage2.png)

The example below saves to:  ComfyUI\output\MyProjects\New_Project\Image01__00001_.png

Image(prefix)01(slot)__00001(comfyui naming/image_index)
![Save Image](/images/saveimage.png)
---
### Visual Image Loader

This node allows you to set a folder and then select images based on thumbnails. Good for projects using a single reference folder with m,ultiple images.  Stays persistantly open untiol you close it. The image selected is automatically populated with a single click.

![Save Image](/images/visual_image_loader.png)

---
### Image Info / Qwen Prep

A look at the `EG Tools/Image` node's interface. You can see the inputs, outputs, and the parameters that control its two modes: simple dimension reporting and advanced image preparation for vision models.

![Image Info Node Interface](/images/qwen_info.png)
---
### Get & Set Tools
This set passes data without wires.  They also autoset the title based on your set "Key" and show the data being passed from and to each other.

![Image Info Node Interface](/images/getsetvalue.png)

---
### Smart Switches in Action

The `Smart Switch` nodes allow you to dynamically select from multiple inputs. This image shows an `INT` switch where `input_3` is currently the active output, demonstrating how you can route different values or data types through a single node.

![Smart Switch Selection](/images/smart_switches.png)
---
### Samples of the Smart Switch Family

For your convenience, EG_Tools provides a `Smart Switch` for every major data type in ComfyUI. This allows you to route images, models, prompts, and more without having to rewire your entire workflow.

![Smart Switch Node Collection](/images/smart_switches2.png)

---
### Workflow Example

![Smart Switch Node Collection](/images/workflow_example.png)
---
## Installation

From your ComfyUI `custom_nodes` directory:

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/egormly/ComfyUI-EG_Tools.git

```

### Updating
If you installed via Git (recommended):
Navigate to `ComfyUI/custom_nodes/ComfyUI-EG_Tools` in your terminal/file manager and run:

```bash
git pull
```
Restart ComfyUI completely (or click "Refresh" in the Manager).

That’s it — no need to re-download anything.