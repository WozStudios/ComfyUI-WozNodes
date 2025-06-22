import torch
import numpy as np
from PIL import Image, ImageOps
import json
import os

from comfy.cli_args import args
import folder_paths


class CreateImageBatch:
    """
    A node to create a batch of images from scratch, with interactive UI.
    """

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "width": ("INT", {"default": 512, "min": 64, "max": 4096, "step": 8}),
                "height": ("INT", {"default": 512, "min": 64, "max": 4096, "step": 8}),
                "batch_size": ("INT", {"default": 4, "min": 1, "max": 64, "step": 1}),
                "image_data": ("STRING", {"multiline": False, "default": "[]"}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "create_batch"
    CATEGORY = "woz/Image/Batch"

    def create_batch(self, width, height, batch_size, image_data):
        try:
            data = json.loads(image_data)
        except Exception as e:
            print(f"Error parsing image_data JSON: {e}")
            return (torch.zeros((0, height, width, 3), dtype=torch.float32, device="cpu"),)

        image_tensors = []

        if len(data) != batch_size:
            print(
                f"Warning: image_data length ({len(data)}) does not match batch_size ({batch_size}). Truncating or padding.")
            default_item = {"type": "color", "value": "#000000"}
            data = (data + [default_item] * batch_size)[:batch_size]

        for item in data:
            if item.get("type") == "color":
                color = item.get("value", "#000000")
                image = Image.new("RGB", (width, height), color)

            elif item.get("type") == "file":
                filename = item.get("value")
                if not filename:
                    image = Image.new("RGB", (width, height), "#FF00FF")  # Magenta for missing file
                else:
                    image_path = folder_paths.get_annotated_filepath(filename)
                    try:
                        img_loaded = Image.open(image_path)
                        img_loaded = img_loaded.convert("RGB")
                        image = ImageOps.fit(img_loaded, (width, height), Image.LANCZOS)
                    except Exception as e:
                        print(f"Error loading image '{filename}': {e}")
                        image = Image.new("RGB", (width, height), "#FF0000")  # Red for error
            else:
                image = Image.new("RGB", (width, height), "#000000")

            tensor = np.array(image).astype(np.float32) / 255.0
            tensor = torch.from_numpy(tensor)[None,]
            image_tensors.append(tensor)

        if not image_tensors:
            print("Warning: Create Image Batch resulted in an empty batch.")
            return (torch.zeros((0, height, width, 3), dtype=torch.float32, device="cpu"),)

        batch_tensor = torch.cat(image_tensors, dim=0)

        print(f"Create Image Batch: Created a batch of {batch_tensor.shape[0]} images.")
        return (batch_tensor,)