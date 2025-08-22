import torch
from transformers import CLIPSegProcessor, CLIPSegForImageSegmentation
from PIL import Image
import numpy as np
import cv2
import time
from constants import (
    RGB_IMAGE_PATH, WOOD_REFERENCE_PATH, WOOD_PANEL_MASK_PATH, 
    WOOD_PANEL_DEPTH_PATH, DEPTH_MAP_PATH, CLIPSEG_MODEL, SEGMENTATION_THRESHOLD
)

start_time = time.time()

# Load the RGB image (from file, as saved by cam_output.py)
rgb_image = Image.open(RGB_IMAGE_PATH).convert("RGB")

# Load CLIPSeg model and processor
processor = CLIPSegProcessor.from_pretrained(CLIPSEG_MODEL)
model = CLIPSegForImageSegmentation.from_pretrained(CLIPSEG_MODEL)

use_text_prompt = False
text_prompt = "one connected, thin, brown cardboard"
reference_image = Image.open(WOOD_REFERENCE_PATH).convert("RGB")

if use_text_prompt:
    inputs = processor(text=text_prompt, images=rgb_image, return_tensors="pt")
else:
    inputs = processor(images=[rgb_image], conditional_images=reference_image, return_tensors="pt")

with torch.no_grad():
   outputs = model(**inputs)
   mask = outputs.logits[0]  # shape: (352, 352)

# Convert mask to numpy and resize to original image size
mask_np = torch.sigmoid(mask).cpu().numpy()
mask_resized = cv2.resize(mask_np, rgb_image.size, interpolation=cv2.INTER_LINEAR)

# Threshold to get binary mask
mask_binary = (mask_resized > SEGMENTATION_THRESHOLD).astype(np.uint8) * 255

# Save the mask
cv2.imwrite(WOOD_PANEL_MASK_PATH, mask_binary)
print(f"Segmentation mask saved as {WOOD_PANEL_MASK_PATH}")

# Load the depth map
# (Assume depth_map.png is the normalized depth map saved by cam_output.py)
depth_map = cv2.imread(DEPTH_MAP_PATH, cv2.IMREAD_UNCHANGED)

# Ensure mask and depth map are the same size
if depth_map.shape[:2] != mask_binary.shape:
   mask_binary_resized = cv2.resize(mask_binary, (depth_map.shape[1], depth_map.shape[0]), interpolation=cv2.INTER_NEAREST)
else:
   mask_binary_resized = mask_binary

# Apply mask: where if condition is true (mask_binary_resized == 255), keep depth value, otherwise set background to 0
wood_panel_depth = np.where(mask_binary_resized == 255, depth_map, 0).astype(depth_map.dtype)

# Save the masked depth map
cv2.imwrite(WOOD_PANEL_DEPTH_PATH, wood_panel_depth)
print(f"Wood panel depth map saved as {WOOD_PANEL_DEPTH_PATH}")

end_time = time.time()

elapsed_time = end_time - start_time
print(f"Script execution time: {elapsed_time:.2f} seconds")