import cv2
import numpy as np

# Example OAK-D Lite intrinsics (adjust for your camera for best results)
# These are for 400P (640x400) resolution
fx = 461.9  # Focal length in pixels
fy = 461.9
cx = 320.0  # Principal point in pixels
cy = 200.0

# Depth scale: if your depth map is in millimeters, set to 0.001 for meters
DEPTH_SCALE = 0.001

# Load depth map
depth_map = cv2.imread('wood_panel_depth_map.png', cv2.IMREAD_UNCHANGED)
if depth_map is None:
    raise FileNotFoundError('wood_panel_depth_map.png not found or could not be loaded.')

height, width = depth_map.shape

# Generate point cloud
points = []
for v in range(height):
    for u in range(width):
        d = depth_map[v, u]
        if d == 0:
            continue  # skip invalid depth
        z = d * DEPTH_SCALE
        x = (u - cx) * z / fx
        y = (v - cy) * z / fy
        points.append((x, y, z))

# Save to PLY file
def save_ply(filename, points):
    with open(filename, 'w') as f:
        f.write('ply\n')
        f.write('format ascii 1.0\n')
        f.write(f'element vertex {len(points)}\n')
        f.write('property float x\n')
        f.write('property float y\n')
        f.write('property float z\n')
        f.write('end_header\n')
        for p in points:
            f.write(f'{p[0]} {p[1]} {p[2]}\n')

save_ply('point_cloud.ply', points)
print(f"Saved {len(points)} points to point_cloud.ply")
