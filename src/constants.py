"""
Constants file for Wood Warping Detection System
Contains camera intrinsics, file paths, and configuration values
"""

# OAK-D Lite Camera Intrinsics
# These values are for 400P resolution (640x400)
# To get camera's exact intrinsics, run calibration script
OAK_D_LITE_INTRINSICS = {
    'fx': 461.9,  # Horizontal focal length in pixels
    'fy': 461.9,  # Vertical focal length in pixels
    'cx': 320.0,  # Principal point X coordinate in pixels
    'cy': 200.0,  # Principal point Y coordinate in pixels
}

# Depth scale configuration
# If your depth map is in millimeters, set to 0.001 for meters
DEPTH_SCALE = 0.001

# File paths
RGB_IMAGE_PATH = "rgb_image.png"
DEPTH_MAP_PATH = "depth_map.png"
WOOD_REFERENCE_PATH = "wood_reference.png"
WOOD_PANEL_MASK_PATH = "wood_panel_mask.png"
WOOD_PANEL_DEPTH_PATH = "wood_panel_depth_map.png"
POINT_CLOUD_PATH = "point_cloud.ply"
DEVIATIONS_PATH = "deviations.txt"

# CLIPSeg configuration
CLIPSEG_MODEL = "CIDAS/clipseg-rd64-refined"
SEGMENTATION_THRESHOLD = 0.5  # Threshold for binary mask (0.0 to 1.0)

# Deviation analysis configuration
DEVIATION_THRESHOLD = 0.001  # meters - threshold for determining if wood is warped

TEXT_OR_IMAGE = True
TEXT_PROMPT = "one brown, curvy cardboard"

# Camera socket mapping (new naming convention)
CAMERA_SOCKETS = {
    'rgb': 'CAM_A',     # RGB camera socket
    'left': 'CAM_B',    # Left mono camera socket  
    'right': 'CAM_C',   # Right mono camera socket
}

# Camera resolution settings
CAMERA_RESOLUTION = {
    'rgb': 'THE_1080_P',      # RGB camera resolution
    'mono': 'THE_400_P',      # Mono camera resolution for depth. Using 400P because it's faster for data processing and resolution is good
    # Alternative options:
    # 'mono': 'THE_800_P',    # Higher resolution, slower processing
    # 'mono': 'THE_720_P',    # Alternative high resolution
}

# Stereo depth configuration
STEREO_DEPTH_CONFIG = {
    'preset': 'HIGH_DENSITY',  # HIGH_DENSITY, MEDIUM_DENSITY, HIGH_ACCURACY
    'left_right_check': True,
    'extended_disparity': True,
    'subpixel': True,
}
