import torch
from transformers import CLIPSegProcessor, CLIPSegForImageSegmentation
from PIL import Image
import numpy as np
import cv2
import time
import warnings
from constants import (
    RGB_IMAGE_PATH, WOOD_REFERENCE_PATH, WOOD_PANEL_MASK_PATH, 
    WOOD_PANEL_DEPTH_PATH, DEPTH_MAP_PATH, CLIPSEG_MODEL, SEGMENTATION_THRESHOLD
)

# Suppress CLIPSeg processor warnings
warnings.filterwarnings("ignore", category=UserWarning, module="transformers")

start_time = time.time()

print("=" * 50)
print("Wood Panel Segmentation with CLIPSeg")
print("=" * 50)

# Load the RGB image (from file, as saved by cam_output.py)
print("\n1. Loading RGB image...")
try:
    rgb_image = Image.open(RGB_IMAGE_PATH).convert("RGB")
    print(f"✓ Loaded RGB image: {rgb_image.size}")
except Exception as e:
    print(f"✗ Error loading RGB image: {e}")
    exit(1)

# Load CLIPSeg model and processor
print("\n2. Loading CLIPSeg model...")
try:
    processor = CLIPSegProcessor.from_pretrained(CLIPSEG_MODEL)
    model = CLIPSegForImageSegmentation.from_pretrained(CLIPSEG_MODEL)
    print("✓ CLIPSeg model loaded successfully")
except Exception as e:
    print(f"✗ Error loading CLIPSeg model: {e}")
    exit(1)

# Configuration
use_text_prompt = False  # Switch to text prompt as it's more reliable
text_prompt = "one connected, thin, brown cardboard"

print(f"\n3. Running segmentation...")
if use_text_prompt:
    print(f"Using text prompt: '{text_prompt}'")
else:
    print("Using reference image for segmentation")
    try:
        reference_image = Image.open(WOOD_REFERENCE_PATH).convert("RGB")
        print(f"✓ Loaded reference image: {reference_image.size}")
    except Exception as e:
        print(f"✗ Error loading reference image: {e}")
        exit(1)

# Prepare inputs for CLIPSeg
try:
    if use_text_prompt:
        # Use text prompt - more reliable approach
        inputs = processor(text=[text_prompt], images=[rgb_image], return_tensors="pt")
    else:
        # Use image prompt - prepare both images separately
        encoded_image = processor(images=[rgb_image], return_tensors="pt")
        encoded_prompt = processor(images=[reference_image], return_tensors="pt")
    
    print("✓ Inputs prepared for CLIPSeg")
except Exception as e:
    print(f"✗ Error preparing inputs: {e}")
    exit(1)

# Run segmentation
try:
    with torch.no_grad():
        if use_text_prompt:
            outputs = model(**inputs)
        else:
            outputs = model(**encoded_image, conditional_pixel_values=encoded_prompt.pixel_values)
        mask = outputs.logits[0]  # shape: (352, 352)
    
    print("✓ Segmentation completed")
except Exception as e:
    print(f"✗ Error during segmentation: {e}")
    exit(1)

# Convert mask to numpy and resize to original image size
print("\n4. Processing segmentation mask...")
mask_np = torch.sigmoid(mask).cpu().numpy()
mask_resized = cv2.resize(mask_np, rgb_image.size, interpolation=cv2.INTER_LINEAR)

# Threshold to get binary mask
mask_binary = (mask_resized > SEGMENTATION_THRESHOLD).astype(np.uint8) * 255
print(f"✓ Applied threshold: {SEGMENTATION_THRESHOLD}")

# Save the mask
cv2.imwrite(WOOD_PANEL_MASK_PATH, mask_binary)
print(f"✓ Segmentation mask saved: {WOOD_PANEL_MASK_PATH}")

# Load the depth map
print("\n5. Loading depth map...")
try:
    depth_map = cv2.imread(DEPTH_MAP_PATH, cv2.IMREAD_UNCHANGED)
    if depth_map is None:
        raise FileNotFoundError(f"Could not load depth map from {DEPTH_MAP_PATH}")
    print(f"✓ Loaded depth map: {depth_map.shape}")
except Exception as e:
    print(f"✗ Error loading depth map: {e}")
    exit(1)

# Ensure mask and depth map are the same size
print("\n6. Applying mask to depth map...")
if depth_map.shape[:2] != mask_binary.shape:
    mask_binary_resized = cv2.resize(mask_binary, (depth_map.shape[1], depth_map.shape[0]), interpolation=cv2.INTER_NEAREST)
    print(f"✓ Resized mask from {mask_binary.shape} to {mask_binary_resized.shape}")
else:
    mask_binary_resized = mask_binary
    print("✓ Mask and depth map sizes match")

# Apply mask: where if condition is true (mask_binary_resized == 255), keep depth value, otherwise set background to 0
wood_panel_depth = np.where(mask_binary_resized == 255, depth_map, 0).astype(depth_map.dtype)

# Count segmented pixels
wood_pixels = np.count_nonzero(mask_binary_resized == 255)
total_pixels = mask_binary_resized.size
percentage = (wood_pixels / total_pixels) * 100
print(f"✓ Wood panel coverage: {wood_pixels}/{total_pixels} pixels ({percentage:.1f}%)")

# Save the masked depth map
cv2.imwrite(WOOD_PANEL_DEPTH_PATH, wood_panel_depth)
print(f"✓ Masked depth map saved: {WOOD_PANEL_DEPTH_PATH}")

end_time = time.time()
elapsed_time = end_time - start_time

print(f"\n Segmentation completed successfully!")
print(f"Generated files:")
print(f"  - {WOOD_PANEL_MASK_PATH}")
print(f"  - {WOOD_PANEL_DEPTH_PATH}")
print(f"Execution time: {elapsed_time:.2f} seconds")