"""
Script to get actual camera intrinsics from OAK-D Lite
Run this once to get your camera's exact calibration values
"""

import depthai as dai
import json

def get_camera_intrinsics():
    """Get camera intrinsics from connected OAK-D Lite"""
    
    pipeline = dai.Pipeline()
    
    try:
        with dai.Device(pipeline) as device:
            print("✓ Connected to OAK-D Lite")
            
            # Get calibration data
            calib_data = device.readCalibration()
            
            # Get intrinsics for left mono camera (used for depth)
            # Using 400P resolution as default
            intrinsics = calib_data.getCameraIntrinsics(
                dai.CameraBoardSocket.LEFT, 
                dai.MonoCameraProperties.SensorResolution.THE_400_P
            )
            
            # Extract the values
            fx = intrinsics[0][0]
            fy = intrinsics[1][1]
            cx = intrinsics[0][2]
            cy = intrinsics[1][2]
            
            print(f"\nYour OAK-D Lite intrinsics (400P resolution):")
            print(f"fx: {fx:.1f}")
            print(f"fy: {fy:.1f}")
            print(f"cx: {cx:.1f}")
            print(f"cy: {cy:.1f}")
            
            return {
                'fx': fx,
                'fy': fy,
                'cx': cx,
                'cy': cy
            }
            
    except Exception as e:
        print(f"✗ Error getting camera intrinsics: {e}")
        print("Make sure your OAK-D Lite is connected and recognized")
        return None

def update_constants_file(intrinsics):
    """Update the constants.py file with actual intrinsics"""
    
    if intrinsics is None:
        print("No intrinsics to update")
        return
    
    try:
        # Read the current constants file
        with open('src/constants.py', 'r') as f:
            content = f.read()
        
        # Update the intrinsics dictionary
        old_intrinsics = "OAK_D_LITE_INTRINSICS = {\n    'fx': 461.9,  # Horizontal focal length in pixels\n    'fy': 461.9,  # Vertical focal length in pixels\n    'cx': 320.0,  # Principal point X coordinate in pixels\n    'cy': 200.0,  # Principal point Y coordinate in pixels\n}"
        
        new_intrinsics = f"""OAK_D_LITE_INTRINSICS = {{
    'fx': {intrinsics['fx']:.1f},  # Horizontal focal length in pixels
    'fy': {intrinsics['fy']:.1f},  # Vertical focal length in pixels
    'cx': {intrinsics['cx']:.1f},  # Principal point X coordinate in pixels
    'cy': {intrinsics['cy']:.1f},  # Principal point Y coordinate in pixels
}}"""
        
        # Replace in content
        updated_content = content.replace(old_intrinsics, new_intrinsics)
        
        # Write back to file
        with open('src/constants.py', 'w') as f:
            f.write(updated_content)
        
        print("✓ Updated src/constants.py with your camera's intrinsics")
        
    except Exception as e:
        print(f"✗ Error updating constants file: {e}")

def main():
    """Main function to get and update camera intrinsics"""
    print("=" * 50)
    print("OAK-D Lite Camera Intrinsics Calibration")
    print("=" * 50)
    
    # Get intrinsics from camera
    intrinsics = get_camera_intrinsics()
    
    if intrinsics:
        # Update constants file
        update_constants_file(intrinsics)
        
        print("\n✓ Calibration complete!")
        print("Your camera intrinsics have been saved to src/constants.py")
        print("You can now run depth_to_cloud.py with accurate intrinsics")
    else:
        print("\n✗ Calibration failed")
        print("Please check your camera connection and try again")

if __name__ == "__main__":
    main()
