# ComfyUI CLAHE Preprocessor

A ComfyUI custom node that applies a CLAHE preprocessing pipeline to optimize images for 3D mesh generation with TRELLIS.

## Why?

Color artifacts in rendered or photographic images — warm ember glows, specular highlights, strong hue gradients — get misinterpreted as geometric features by depth estimation models. A specular highlight line across a cheek becomes a sharp geometric edge in the mesh. This node strips those artifacts before they reach TRELLIS.

## Pipeline

The node applies four processing steps in order:

1. **Weighted grayscale conversion** — 15% Red, 65% Green, 20% Blue (configurable). The green channel carries the best structural detail; the red channel is dominated by warm glow artifacts.
2. **Specular suppression** — Pixels above the 90th percentile brightness are blended toward a Gaussian-blurred local average, flattening specular highlights without destroying texture contrast.
3. **CLAHE** (Contrast Limited Adaptive Histogram Equalization) — Boosts local texture contrast (bark, skin pores, fabric weave) without amplifying broad highlights. Default: clipLimit=3.0, tileGridSize=8x8.
4. **3-channel RGB output** — Converts the grayscale result back to 3-channel RGB. TRELLIS requires this; single-channel images cause a `TypeError` in tensor conversion.

## Node Inputs

| Input | Type | Default | Description |
|---|---|---|---|
| image | IMAGE | — | Input image |
| red_weight | FLOAT | 0.15 | Red channel contribution to grayscale |
| green_weight | FLOAT | 0.65 | Green channel contribution |
| blue_weight | FLOAT | 0.20 | Blue channel contribution |
| specular_percentile | FLOAT | 90.0 | Brightness threshold percentile for suppression |
| specular_blur | INT | 21 | Gaussian blur kernel size (must be odd) |
| clip_limit | FLOAT | 3.0 | CLAHE clip limit |
| tile_size | INT | 8 | CLAHE tile grid size |

## Features

- **Live preview** — Processed image displays directly on the node
- **Auto-update** — Preview re-renders automatically when any parameter changes (500ms debounce)
- **Batch support** — Handles batched image tensors

## Installation

Clone into your ComfyUI custom nodes directory:

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/YOUR_USERNAME/ComfyUI-CLAHE-Preprocessor.git
```

OpenCV is the only dependency not bundled with ComfyUI:

```bash
pip install opencv-python
```

Restart ComfyUI. The node appears under **image/preprocessing** as **CLAHE Preprocess (TRELLIS)**.

## Requirements

- ComfyUI with V3 API support (`comfy_api.latest`)
- Python 3.10+
- opencv-python >= 4.8.0
