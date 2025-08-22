import cv2
import numpy as np
import time
from constants import OAK_D_LITE_INTRINSICS, DEPTH_SCALE, WOOD_PANEL_DEPTH_PATH, POINT_CLOUD_PATH

start_time = time.time()

# Get camera intrinsics from constants (no need to connect to camera every time)
fx = OAK_D_LITE_INTRINSICS['fx']  # Focal Length X
fy = OAK_D_LITE_INTRINSICS['fy']  # Focal Length Y
cx = OAK_D_LITE_INTRINSICS['cx']  # Principal Point X (center of the image)
cy = OAK_D_LITE_INTRINSICS['cy']  # Principal Point Y

# Load depth map
depth_map = cv2.imread(WOOD_PANEL_DEPTH_PATH, cv2.IMREAD_UNCHANGED)
if depth_map is None:
   raise FileNotFoundError(f'{WOOD_PANEL_DEPTH_PATH} not found or could not be loaded.')

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

save_ply(POINT_CLOUD_PATH, points)
print(f"Saved {len(points)} points to {POINT_CLOUD_PATH}")

end_time = time.time()
elapsed_time = end_time - start_time
print(f"Execution time: {elapsed_time:.2f} seconds")