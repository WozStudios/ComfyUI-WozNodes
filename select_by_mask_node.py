import torch


class ImageBatchSelectByMask:
    """
    A node that selects images from one of two batches (A or B) based on a
    corresponding mask batch.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images_a": ("IMAGE",),
                "images_b": ("IMAGE",),
                "masks": ("IMAGE",),
            },
            "optional": {
                "threshold": ("FLOAT", {
                    "default": 0.5,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "display": "slider"
                }),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("selected_images",)
    FUNCTION = "select"
    CATEGORY = "woz/Image/Batch"

    def select(self, images_a, images_b, masks, threshold=0.5):
        batch_a_size = images_a.shape[0]
        batch_b_size = images_b.shape[0]
        mask_batch_size = masks.shape[0]

        min_batch_size = min(batch_a_size, batch_b_size, mask_batch_size)

        if min_batch_size == 0:
            print("Warning: One of the input batches to Select By Mask is empty. Returning an empty batch.")
            return (torch.zeros((0, images_a.shape[1], images_a.shape[2], images_a.shape[3]), dtype=images_a.dtype,
                                device=images_a.device),)

        if not (batch_a_size == batch_b_size == mask_batch_size):
            print(
                f"Warning: Select By Mask input batches have different sizes ({batch_a_size}, {batch_b_size}, {mask_batch_size}). "
                f"Processing up to the shortest length: {min_batch_size}.")

        if images_a.shape[1:] != images_b.shape[1:]:
            print(f"Warning: Select By Mask 'images_a' and 'images_b' have different dimensions "
                  f"({images_a.shape[1:]} vs {images_b.shape[1:]}). This may cause issues in downstream nodes.")

        output_images = []

        for i in range(min_batch_size):
            mask_image = masks[i]

            if mask_image.shape[-1] == 3:  # RGB
                mask_luminance = 0.299 * mask_image[..., 0] + 0.587 * mask_image[..., 1] + 0.114 * mask_image[..., 2]
            else:  # Grayscale or other
                mask_luminance = mask_image[..., 0]

            mean_value = torch.mean(mask_luminance)

            if mean_value < threshold:
                selected_image = images_a[i]
            else:
                selected_image = images_b[i]

            output_images.append(selected_image.unsqueeze(0))

        final_batch = torch.cat(output_images, dim=0)

        print(f"Select By Mask: Processed {min_batch_size} images. Final batch size: {final_batch.shape[0]}.")

        return (final_batch,)