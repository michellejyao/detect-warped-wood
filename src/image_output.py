import os
import sys
import time
import cv2
import numpy as np
import time
import depthai as dai

def detect_camera(dai):
    """Detect if OAK-D Lite camera is connected."""
    try:
        devices = dai.Device.getAllConnectedDevices()
        if not devices:
            print("No OAK-D devices found")
            return None
        
        print(f"Found {len(devices)} OAK-D device")
        return devices[0]  # Return first device
    except Exception as e:
        print(f"Error detecting camera: {e}")
        return None

def create_camera_pipeline(dai):
    """Create a pipeline for RGB and depth map capture."""
    try:
        pipeline = dai.Pipeline()
        
        # Create RGB camera node, adding color camera properties
       rgb_cam = pipeline.create(dai.node.ColorCamera)
       rgb_cam.setBoardSocket(dai.CameraBoardSocket.RGB)
       rgb_cam.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
       rgb_cam.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)
       rgb_cam.setInterleaved(False)
      
       # Create stereo depth nodes
       left_cam = pipeline.create(dai.node.MonoCamera)
       left_cam.setBoardSocket(dai.CameraBoardSocket.LEFT)
       left_cam.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
      
       right_cam = pipeline.create(dai.node.MonoCamera)
       right_cam.setBoardSocket(dai.CameraBoardSocket.RIGHT)
       right_cam.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
      
       stereo = pipeline.create(dai.node.StereoDepth) # Create stereo depth node
       stereo.setDefaultProfilePreset(dai.node.StereoDepth.PresetMode.HIGH_DENSITY) # Sets the quality profile for depth calculation. HIGH_DENSITY prioritizes depth resolution over speed
       stereo.setLeftRightCheck(True) # Enables left-right consistency check
       stereo.setExtendedDisparity(True) # Extends the search range to handle objects closer to the camera
       stereo.setSubpixel(True) # Enables subpixel (non-integer pixel value) accuracy for depth calculation.
       # stereo.setDepthAlign(dai.CameraBoardSocket.RGB)
      
       # Create output nodes
       rgb_out = pipeline.create(dai.node.XLinkOut)
       rgb_out.setStreamName("rgb")
      
       depth_out = pipeline.create(dai.node.XLinkOut)
       depth_out.setStreamName("depth")
      
       # Link nodes
       rgb_cam.video.link(rgb_out.input)
       left_cam.out.link(stereo.left)
       right_cam.out.link(stereo.right)
       stereo.depth.link(depth_out.input)
      
       print("Camera pipeline created successfully")
       return pipeline
      
    except Exception as e:
        print(f"Failed to create pipeline: {e}")
        return None
    
def capture_images(device, pipeline):
   """Capture RGB and depth images from the camera."""
   try:
       print("Starting camera pipeline...")
       device.startPipeline(pipeline)
      
       # Get output queues
       rgb_queue = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
       depth_queue = device.getOutputQueue(name="depth", maxSize=4, blocking=False)
      
       print("Waiting for camera to stabilize.")
       time.sleep(2)  # Give camera time to adjust
      
       print("Capturing images")
       rgb_frame = None
       depth_frame = None
      
       # Wait for both frames
       start_time = time.time()
       timeout = 10  # seconds
      
       while time.time() - start_time < timeout:
           rgb_packet = rgb_queue.tryGet()
           depth_packet = depth_queue.tryGet()
          
           if rgb_packet is not None:
               rgb_frame = rgb_packet.getCvFrame()
               print("RGB frame captured")
          
           if depth_packet is not None:
               depth_frame = depth_packet.getFrame()
               print("Depth frame captured")
          
           if rgb_frame is not None and depth_frame is not None:
               break
          
           time.sleep(0.1)
      
       if rgb_frame is None or depth_frame is None:
           print("Failed to capture frames within timeout")
           return None, None
      
       return rgb_frame, depth_frame
      
   except Exception as e:
       print(f"Error capturing images: {e}")
       return None, None


def save_images(rgb_frame, depth_frame):
   """Save captured images to disk."""
   try:
       timestamp = time.strftime("%Y%m%d_%H%M%S")
      
       # Save RGB image
       rgb_filename = f"rgb_image.png"
       cv2.imwrite(rgb_filename, rgb_frame)
       print(f"✓ RGB image saved: {rgb_filename}")
      
       # Normalize depth for visualization and save
       depth_normalized = cv2.normalize(depth_frame, None, 0, 255, cv2.NORM_MINMAX)
       depth_normalized = np.uint8(depth_normalized)
      
       depth_filename = f"depth_map.png"
       cv2.imwrite(depth_filename, depth_normalized)
       print(f"✓ Depth image saved: {depth_filename}")
      
       # Save raw depth data as numpy array
       depth_raw_filename = f"test_depth_raw_{timestamp}.npy"
       np.save(depth_raw_filename, depth_frame)
       print(f"✓ Raw depth data saved: {depth_raw_filename}")
      
       return True
      
   except Exception as e:
       print(f"✗ Error saving images: {e}")
       return False

def main():
   print("Creating camera pipeline.")
   pipeline = create_camera_pipeline(dai)
   if not pipeline:
       sys.exit(1)
  
   # Connect to device
   print("Connecting to camera.")
   try:
       with dai.Device(device_info) as device:
           print("Connected to camera successfully.")
          
           # Capture images
           print("Capturing images")
           rgb_frame, depth_frame = capture_images(device, pipeline)
          
           if rgb_frame is not None and depth_frame is not None:
               print(f"Captured RGB frame: {rgb_frame.shape}")
               print(f"Captured depth frame: {depth_frame.shape}")
              
               # Save images
               print("Saving images")
               if save_images(rgb_frame, depth_frame):
                   print("Camera test completed successfully!")
                   print("Check the generated image files in the current directory.")
               else:
                   print("\n⚠️  Camera test completed with errors saving images.")
           else:
               print("Failed to capture images from camera.")
              
   except Exception as e:
       print(f"Error connecting to camera: {e}")
       sys.exit(1)

if __name__ == "__main__":
   start_time = time.time()
   main()
   end_time = time.time()

   elapsed_time = end_time - start_time
   print(f"Script execution time: {elapsed_time:.2f} seconds")