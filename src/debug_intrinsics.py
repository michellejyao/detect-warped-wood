"""
Debug script to understand why camera intrinsics are returning small values
and get the correct pixel-based intrinsics for OAK-D Lite
"""

import depthai as dai

def debug_camera_intrinsics():
    """Debug camera intrinsics to understand the coordinate system"""
    
    pipeline = dai.Pipeline()
    
    try:
        with dai.Device(pipeline) as device:
            print("✓ Connected to OAK-D Lite")
            
            # Get calibration data
            calib_data = device.readCalibration()
            
            print("\n=== Camera Information ===")
            
            # Check available cameras (using newer naming convention)
            cameras = [
                dai.CameraBoardSocket.CAM_B,  # Left mono camera
                dai.CameraBoardSocket.CAM_C,  # Right mono camera
                dai.CameraBoardSocket.CAM_A   # RGB camera
            ]
            
            resolutions = [
                dai.MonoCameraProperties.SensorResolution.THE_400_P,
                dai.MonoCameraProperties.SensorResolution.THE_800_P,
                dai.ColorCameraProperties.SensorResolution.THE_1080_P
            ]
            
            for camera in cameras:
                print(f"\nCamera: {camera}")
                for resolution in resolutions:
                    try:
                        # Get intrinsics (skip resolution check for now)
                        intrinsics = calib_data.getCameraIntrinsics(camera, resolution)
                        print(f"  Intrinsics {resolution}:")
                        print(f"    fx: {intrinsics[0][0]:.6f}")
                        print(f"    fy: {intrinsics[1][1]:.6f}")
                        print(f"    cx: {intrinsics[0][2]:.6f}")
                        print(f"    cy: {intrinsics[1][2]:.6f}")
                        
                        # Check if these look like pixel coordinates
                        if intrinsics[0][0] > 100 and intrinsics[1][1] > 100:
                            print(f"    ✓ These look like pixel coordinates!")
                        else:
                            print(f"    ⚠ These look like normalized coordinates")
                            
                    except Exception as e:
                        print(f"    Error with {resolution}: {e}")
            
            # Try to get extrinsics as well
            print("\n=== Extrinsics ===")
            try:
                extrinsics = calib_data.getCameraExtrinsics(
                    dai.CameraBoardSocket.CAM_B,  # Left mono camera
                    dai.CameraBoardSocket.CAM_A   # RGB camera
                )
                print("Left to RGB extrinsics:")
                print(extrinsics)
            except Exception as e:
                print(f"Error getting extrinsics: {e}")
                
    except Exception as e:
        print(f"✗ Error: {e}")

def get_pixel_intrinsics():
    """Try to get pixel-based intrinsics"""
    
    pipeline = dai.Pipeline()
    
    try:
        with dai.Device(pipeline) as device:
            calib_data = device.readCalibration()
            
            # Try different approaches to get pixel intrinsics
            print("\n=== Trying to get pixel intrinsics ===")
            
            # Method 1: Direct intrinsics
            intrinsics = calib_data.getCameraIntrinsics(
                dai.CameraBoardSocket.CAM_B,  # Left mono camera
                dai.MonoCameraProperties.SensorResolution.THE_400_P
            )
            
            # Method 2: Use standard 400P resolution (640x400)
            # Since getCameraResolution doesn't exist, use known values
            width, height = 640, 400  # Standard 400P resolution
            print(f"Using standard 400P resolution: {width}x{height}")
            
            print(f"Image dimensions: {width}x{height}")
            print(f"Raw intrinsics fx: {intrinsics[0][0]:.6f}")
            print(f"Raw intrinsics fy: {intrinsics[1][1]:.6f}")
            print(f"Raw intrinsics cx: {intrinsics[0][2]:.6f}")
            print(f"Raw intrinsics cy: {intrinsics[1][2]:.6f}")
            
            # If these are normalized, convert to pixels
            if intrinsics[0][0] < 10:  # Likely normalized
                print("\nConverting normalized to pixel coordinates:")
                fx_pixel = intrinsics[0][0] * width
                fy_pixel = intrinsics[1][1] * height
                cx_pixel = intrinsics[0][2] * width
                cy_pixel = intrinsics[1][2] * height
                
                print(f"Pixel fx: {fx_pixel:.1f}")
                print(f"Pixel fy: {fy_pixel:.1f}")
                print(f"Pixel cx: {cx_pixel:.1f}")
                print(f"Pixel cy: {cy_pixel:.1f}")
                
                return {
                    'fx': fx_pixel,
                    'fy': fy_pixel,
                    'cx': cx_pixel,
                    'cy': cy_pixel
                }
            else:
                print("\nThese appear to be pixel coordinates already")
                return {
                    'fx': intrinsics[0][0],
                    'fy': intrinsics[1][1],
                    'cx': intrinsics[0][2],
                    'cy': intrinsics[1][2]
                }
                
    except Exception as e:
        print(f"✗ Error: {e}")
        return None

def main():
    """Main debug function"""
    print("=" * 60)
    print("OAK-D Lite Camera Intrinsics Debug")
    print("=" * 60)
    
    # Debug all camera information
    debug_camera_intrinsics()
    
    # Try to get pixel intrinsics
    pixel_intrinsics = get_pixel_intrinsics()
    
    if pixel_intrinsics:
        print(f"\n=== Recommended Pixel Intrinsics ===")
        print(f"fx: {pixel_intrinsics['fx']:.1f}")
        print(f"fy: {pixel_intrinsics['fy']:.1f}")
        print(f"cx: {pixel_intrinsics['cx']:.1f}")
        print(f"cy: {pixel_intrinsics['cy']:.1f}")
        
        print(f"\nYou can update src/constants.py with these values")
    else:
        print(f"\n✗ Could not determine pixel intrinsics")

if __name__ == "__main__":
    main()
