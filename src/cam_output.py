import depthai as dai
import cv2
import numpy as np

def main():
    # Create pipeline
    pipeline = dai.Pipeline()

    # Define sources and outputs
    cam_left = pipeline.create(dai.node.MonoCamera)
    cam_right = pipeline.create(dai.node.MonoCamera)
    stereo = pipeline.create(dai.node.StereoDepth)
    
    # Add color camera for RGB
    cam_rgb = pipeline.create(dai.node.ColorCamera)
    cam_rgb.setBoardSocket(dai.CameraBoardSocket.RGB)
    cam_rgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
    cam_rgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)
    cam_rgb.setInterleaved(False)
    
    # Linking
    cam_left.out.link(stereo.left)
    cam_right.out.link(stereo.right)

    # Add output for depth map
    xout_depth = pipeline.create(dai.node.XLinkOut)
    xout_depth.setStreamName("depth")
    stereo.depth.link(xout_depth.input)

    # Add output for RGB
    xout_rgb = pipeline.create(dai.node.XLinkOut)
    xout_rgb.setStreamName("rgb")
    cam_rgb.video.link(xout_rgb.input)

    # Connect to device and start pipeline
    with dai.Device(pipeline) as device:
        depth_queue = device.getOutputQueue(name="depth", maxSize=1, blocking=False)
        rgb_queue = device.getOutputQueue(name="rgb", maxSize=1, blocking=False)
        print("Waiting for depth and RGB frames...")
        depth_frame = None
        rgb_frame = None
        while True:
            in_depth = depth_queue.get()
            in_rgb = rgb_queue.get()
            if in_depth is not None and in_rgb is not None:
                depth_frame = in_depth.getFrame()
                rgb_frame = in_rgb.getCvFrame()
                break

        # Normalize for visualization
        depth_frame_normalized = cv2.normalize(depth_frame, None, 0, 255, cv2.NORM_MINMAX)
        depth_frame_normalized = np.uint8(depth_frame_normalized)

        # Save depth map as PNG
        output_depth_path = "depth_map.png"
        cv2.imwrite(output_depth_path, depth_frame_normalized)
        print(f"Depth map saved to {output_depth_path}")

        # Save RGB image as PNG
        output_rgb_path = "rgb_image.png"
        cv2.imwrite(output_rgb_path, rgb_frame)
        print(f"RGB image saved to {output_rgb_path}")

        yield rgb_frame, depth_frame

if __name__ == "__main__":
    main()
