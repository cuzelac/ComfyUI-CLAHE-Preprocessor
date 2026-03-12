import numpy as np
import cv2
import torch
from comfy_api.latest import io, ui


class CLAHEPreprocess(io.ComfyNode):
    """Applies CLAHE preprocessing pipeline optimized for TRELLIS 3D mesh generation.

    Suppresses color artifacts (orange ember glow, specular highlights) that confuse
    depth estimation, then boosts local texture contrast via CLAHE.
    """

    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="CLAHEPreprocess_TRELLIS",
            display_name="CLAHE Preprocess (TRELLIS)",
            category="image/preprocessing",
            description="CLAHE preprocessing pipeline for improving 3D mesh generation with TRELLIS. "
                        "Converts to weighted grayscale, suppresses specular highlights, applies CLAHE, "
                        "and outputs 3-channel RGB.",
            is_output_node=True,
            inputs=[
                io.Image.Input("image", tooltip="Input image to preprocess"),
                io.Float.Input("red_weight", default=0.15, min=0.0, max=1.0, step=0.01,
                               tooltip="Red channel contribution to grayscale. Low value suppresses warm glow artifacts."),
                io.Float.Input("green_weight", default=0.65, min=0.0, max=1.0, step=0.01,
                               tooltip="Green channel contribution to grayscale. High value preserves structural detail."),
                io.Float.Input("blue_weight", default=0.20, min=0.0, max=1.0, step=0.01,
                               tooltip="Blue channel contribution to grayscale."),
                io.Float.Input("specular_percentile", default=90.0, min=50.0, max=100.0, step=0.5,
                               tooltip="Brightness percentile threshold for specular suppression."),
                io.Int.Input("specular_blur", default=21, min=3, max=51, step=2,
                             tooltip="Gaussian blur kernel size for specular suppression (must be odd)."),
                io.Float.Input("clip_limit", default=3.0, min=0.5, max=10.0, step=0.1,
                               tooltip="CLAHE clip limit. Higher values increase local contrast."),
                io.Int.Input("tile_size", default=8, min=2, max=32, step=1,
                             tooltip="CLAHE tile grid size (used for both dimensions)."),
            ],
            outputs=[
                io.Image.Output("IMAGE"),
            ],
            hidden=[io.Hidden.prompt, io.Hidden.extra_pnginfo],
        )

    @classmethod
    def execute(cls, image, red_weight, green_weight, blue_weight,
                specular_percentile, specular_blur, clip_limit, tile_size):
        # Ensure blur kernel is odd
        if specular_blur % 2 == 0:
            specular_blur += 1

        batch_results = []
        for i in range(image.shape[0]):
            # ComfyUI IMAGE: float32 [0,1] RGB (H,W,C) -> uint8 for OpenCV
            img_np = (image[i].cpu().numpy() * 255).astype(np.uint8)

            # 1. Custom grayscale conversion — weighted channel mix
            # img_np channels are R, G, B (ComfyUI order)
            r, g, b = img_np[:, :, 0], img_np[:, :, 1], img_np[:, :, 2]
            gray = np.clip(
                r.astype(np.float32) * red_weight
                + g.astype(np.float32) * green_weight
                + b.astype(np.float32) * blue_weight,
                0, 255
            ).astype(np.uint8)

            # 2. Specular suppression — blend bright pixels toward blurred local average
            threshold = np.percentile(gray, specular_percentile)
            mask = gray > threshold
            if np.any(mask):
                blurred = cv2.GaussianBlur(gray, (specular_blur, specular_blur), 0)
                gray[mask] = blurred[mask]

            # 3. CLAHE
            clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(tile_size, tile_size))
            result = clahe.apply(gray)

            # 4. Convert single-channel grayscale to 3-channel RGB
            # CRITICAL: TRELLIS requires 3-channel RGB images
            result_rgb = cv2.cvtColor(result, cv2.COLOR_GRAY2RGB)

            # Back to float32 [0,1]
            batch_results.append(result_rgb.astype(np.float32) / 255.0)

        output = torch.from_numpy(np.stack(batch_results))
        return io.NodeOutput(output, ui=ui.PreviewImage(output, cls=cls))
