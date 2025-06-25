# Import the classes from your node files
from .trim_batch_node import ImageBatchTrim
from .create_batch_node import CreateImageBatch
from .select_by_mask_node import ImageBatchSelectByMask
from .image_batcher_by_indexz import ImageBatcherByIndexProV2

# A dictionary that routes internal names to node classes
NODE_CLASS_MAPPINGS = {
    "ImageBatchTrim": ImageBatchTrim,
    "CreateImageBatch": CreateImageBatch,
    "ImageBatchSelectByMask": ImageBatchSelectByMask,
    "ImageBatcherByIndexProV2": ImageBatcherByIndexProV2,
}

# A dictionary that maps internal names to display names
NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageBatchTrim": "Trim Image Batch",
    "CreateImageBatch": "Create Image Batch",
    "ImageBatchSelectByMask": "Select Image Batch by Mask",
    "ImageBatcherByIndexProV2": "Advanced Batch Creator",
}

# This is the important part for the javascript
# It tells ComfyUI to serve the files in the 'js' directory
# The key is the name of your package, and the value is the path to the 'js' directory
WEB_DIRECTORY = "./js"

print("✅ Loaded Image Batch Utils")