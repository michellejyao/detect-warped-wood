import torch
from transformers import CLIPSegProcessor, CLIPSegForImageSegmentation
from PIL import Image
import numpy as np
import cv2

# Load the RGB image (from file, as saved by depth_map.py)
rgb_image_path = "rgb_image.png"
rgb_image = Image.open(rgb_image_path).convert("RGB")

# Load the reference image of a wood panel
reference_image_path = "wood_reference.jpg"
reference_image = Image.open(reference_image_path).convert("RGB")

# Load CLIPSeg model and processor
processor = CLIPSegProcessor.from_pretrained("CIDAS/clipseg-rd64-refined")
model = CLIPSegForImageSegmentation.from_pretrained("CIDAS/clipseg-rd64-refined")

# Prepare inputs for visual prompting (reference image as prompt)
encoded_image = processor(images=[rgb_image], return_tensors="pt")
encoded_prompt = processor(images=[reference_image], return_tensors="pt")

# Run inference
with torch.no_grad():
    outputs = model(**encoded_image, conditional_pixel_values=encoded_prompt.pixel_values)
    mask = outputs.logits[0]  # shape: (352, 352)

# Convert mask to numpy and resize to original image size
mask_np = torch.sigmoid(mask).cpu().numpy()
mask_resized = cv2.resize(mask_np, rgb_image.size, interpolation=cv2.INTER_LINEAR)

# Threshold to get binary mask
mask_binary = (mask_resized > 0.5).astype(np.uint8) * 255

# Save the mask
cv2.imwrite("wood_panel_mask.png", mask_binary)
print("Segmentation mask saved as wood_panel_mask.png")

# Load the depth map
# (Assume depth_map.png is the normalized depth map saved by depth_map.py)
depth_map = cv2.imread("depth_map.png", cv2.IMREAD_UNCHANGED)

# Ensure mask and depth map are the same size
if depth_map.shape[:2] != mask_binary.shape:
    mask_binary_resized = cv2.resize(mask_binary, (depth_map.shape[1], depth_map.shape[0]), interpolation=cv2.INTER_NEAREST)
else:
    mask_binary_resized = mask_binary

# Apply mask: where if condition is true (mask_binary_resized == 255), keep depth value, otherwise set background to 0
wood_panel_depth = np.where(mask_binary_resized == 255, depth_map, 0).astype(depth_map.dtype)

# Save the masked depth map
cv2.imwrite("wood_panel_depth_map.png", wood_panel_depth)
print("Wood panel depth map saved as wood_panel_depth_map.png")
