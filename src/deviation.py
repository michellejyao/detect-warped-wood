import numpy as np

# Load point cloud from PLY file
def load_ply(filename):
    points = []
    with open(filename, 'r') as f:
        header = True
        for line in f:
            if header:
                if line.strip() == 'end_header':
                    header = False
                continue
            parts = line.strip().split()
            if len(parts) >= 3:
                x, y, z = map(float, parts[:3])
                points.append([x, y, z])
    return np.array(points)

# Fit plane to 3D points using least squares (ax + by + c = z)
def fit_plane(points):
    X = points[:, :2]
    X = np.c_[X, np.ones(X.shape[0])]  # [x, y, 1]
    Z = points[:, 2]
    # Solve for [a, b, c] in ax + by + c = z
    coeffs, _, _, _ = np.linalg.lstsq(X, Z, rcond=None)
    return coeffs  # a, b, c

# Calculate vertical deviation from plane
def compute_deviations(points, plane_coeffs):
    a, b, c = plane_coeffs
    z_plane = a * points[:, 0] + b * points[:, 1] + c
    deviations = points[:, 2] - z_plane
    return deviations

if __name__ == "__main__":
    # Parameters
    ply_file = "point_cloud.ply"
    deviation_threshold = 0.005  # meters (adjust as needed)

    # Load points
    points = load_ply(ply_file)
    if points.shape[0] == 0:
        print("No points loaded from point cloud.")
        exit(1)

    # Fit plane
    plane_coeffs = fit_plane(points)
    print(f"Fitted plane: z = {plane_coeffs[0]:.6f}*x + {plane_coeffs[1]:.6f}*y + {plane_coeffs[2]:.6f}")

    # Compute deviations
    deviations = compute_deviations(points, plane_coeffs)
    std_dev = np.std(deviations)
    print(f"Standard deviation of vertical deviations: {std_dev:.6f} meters")

    # Save deviations for inspection
    np.savetxt("deviations.txt", deviations)

    # Determine if warped
    if std_dev > deviation_threshold:
        print(f"Wood panel is WARPED (std dev > {deviation_threshold})")
    else:
        print(f"Wood panel is FLAT (std dev <= {deviation_threshold})")
