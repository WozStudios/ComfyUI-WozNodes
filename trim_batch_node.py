import torch

class ImageBatchTrim:
    """
    A node to trim an image batch by a start and end index.
    """
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE",),
                "start_index": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 9998,
                    "step": 1
                }),
                "end_index": ("INT", {
                    "default": 9999,
                    "min": 1,
                    "max": 9999,
                    "step": 1
                }),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("trimmed_images",)
    FUNCTION = "trim"
    CATEGORY = "woz/Image/Batch"

    def trim(self, images, start_index, end_index):
        batch_size = images.shape[0]
        start = max(0, start_index)
        end = min(batch_size, end_index)

        if start >= end:
            print(f"Warning: Image Batch Trim resulted in an empty batch. Start ({start_index}) is not less than End ({end_index}).")
            empty_batch = torch.zeros((0, images.shape[1], images.shape[2], images.shape[3]), dtype=images.dtype, device=images.device)
            return (empty_batch,)

        trimmed_batch = images[start:end]
        print(f"Image Batch Trim: Original size: {batch_size}, Trimmed to range [{start}:{end}], New size: {trimmed_batch.shape[0]}")
        return (trimmed_batch,)