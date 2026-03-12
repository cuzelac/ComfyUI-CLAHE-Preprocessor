# ComfyUI CLAHE Preprocessor

A ComfyUI custom node that preprocesses images for cleaner depth estimation and 3D reconstruction. Strips color information, suppresses specular highlights, and enhances local texture contrast via CLAHE — giving downstream models structural detail instead of lighting artifacts.

## The Problem

Color and lighting in images often mislead geometry-focused models. Specular highlights get interpreted as sharp edges, color gradients create false depth boundaries, and broad illumination washes out fine surface detail. This is especially problematic for 3D mesh generation (TRELLIS, etc.), depth estimation, and normal map extraction.

## Pipeline

The node applies four processing steps in order:

1. **Weighted grayscale conversion** — Configurable channel mix (default: 15% R, 65% G, 20% B). Lets you emphasize the channel with the best structural detail for your content and suppress channels dominated by lighting artifacts.
2. **Specular suppression** — Pixels above a configurable brightness percentile are blended toward a Gaussian-blurred local average. Flattens highlights without destroying surrounding texture contrast.
3. **CLAHE** (Contrast Limited Adaptive Histogram Equalization) — Boosts local texture contrast (surface detail, fine geometry cues) without amplifying broad highlights. Default: clipLimit=3.0, tileGridSize=8x8.
4. **3-channel RGB output** — Converts the result back to 3-channel RGB so it's compatible with downstream nodes that expect color images (e.g., TRELLIS, which throws a `TypeError` on single-channel input).

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
- **Reset weights** — Button to restore channel weights to defaults
- **Batch support** — Handles batched image tensors

## Use Cases

- Preprocessing for 3D mesh generation (TRELLIS, InstantMesh, etc.)
- Cleaning images for depth estimation models
- Preparing inputs for normal map extraction
- Any pipeline where you want structural detail without color/lighting interference

## Installation

Clone into your ComfyUI custom nodes directory:

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/cuzelac/ComfyUI-CLAHE-Preprocessor.git
```

OpenCV is the only dependency not bundled with ComfyUI:

```bash
pip install opencv-python
```

Restart ComfyUI. The node appears under **image/preprocessing** as **CLAHE Preprocess**.

## Requirements

- ComfyUI with V3 API support (`comfy_api.latest`)
- Python 3.10+
- opencv-python >= 4.8.0
