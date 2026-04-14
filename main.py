"""
Lane Detection and Driver Assistance System
Complete implementation using OpenCV

Main orchestrator that coordinates all modules for real-time
lane detection, curvature estimation, and driver assistance warnings.
"""

import cv2
import yaml
import os
import sys
from datetime import datetime

# Import modules
from video_loader.video_reader import VideoReader, VideoWriter
from preprocessing.image_preprocessor import ImagePreprocessor
from lane_detection.lane_detector import LaneDetector
from curvature_estimation.curvature_calculator import CurvatureCalculator
from vehicle_position.position_estimator import PositionEstimator
from warning_system.lane_warning import LaneWarning
from utils.fps import FPSCounter
from utils.draw import DrawingUtils
from utils.logger import SystemLogger


class LaneDetectionSystem:
    """Main system orchestrator"""
    
    def __init__(self, config_path='config/config.yaml'):
        """
        Initialize the lane detection system
        
        Args:
            config_path: Path to configuration file
        """
        self.project_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(self.project_dir)

        self.logger = SystemLogger().get_logger()
        self.config = self._load_config(self._resolve_path(config_path))
        
        # Initialize components
        self.video_reader = None
        self.video_writer = None
        self.preprocessor = None
        self.lane_detector = None
        self.curvature_calculator = None
        self.position_estimator = None
        self.lane_warning = None
        self.fps_counter = FPSCounter()
        
        self.frame_count = 0
        self.total_frames = 0
        self.window_name = "Lane Detection and Driver Assistance System"
        
        self.logger.info("=" * 70)
        self.logger.info("Lane Detection and Driver Assistance System Initialized")
        self.logger.info("=" * 70)

    def _resolve_path(self, path):
        """Resolve a path relative to the project directory."""
        if path is None:
            return path
        if os.path.isabs(path):
            return path
        return os.path.join(self.project_dir, path)

    def _normalize_kernel(self, kernel_value, default=(5, 5)):
        """Normalize kernel configuration into a 2-item tuple of integers."""
        if isinstance(kernel_value, (list, tuple)) and len(kernel_value) == 2:
            return int(kernel_value[0]), int(kernel_value[1])

        if isinstance(kernel_value, str):
            cleaned = kernel_value.strip().strip('()[]')
            parts = [part.strip() for part in cleaned.split(',') if part.strip()]
            if len(parts) == 2:
                try:
                    return int(parts[0]), int(parts[1])
                except ValueError:
                    pass

        return default
    
    def _load_config(self, config_path):
        """
        Load configuration from YAML file
        
        Args:
            config_path: Path to config file
            
        Returns:
            dict: Configuration dictionary
        """
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            self.logger.info(f"Configuration loaded: {config_path}")
            return config
        except FileNotFoundError:
            self.logger.error(f"Config file not found: {config_path}")
            sys.exit(1)
        except Exception as e:
            self.logger.error(f"Error loading config: {str(e)}")
            sys.exit(1)
    
    def initialize_components(self):
        """Initialize all system components"""
        
        # Initialize video reader
        video_source_config = self.config.get('video_source', 'input/road_video.mp4')
        video_source = self._resolve_path(video_source_config)
        if not isinstance(video_source_config, int) and not os.path.exists(video_source):
            self.logger.warning(
                f"Configured video not found: {video_source}. Falling back to webcam index 0."
            )
            video_source = 0

        self.video_reader = VideoReader(video_source)
        
        if self.video_reader.cap is None or not self.video_reader.cap.isOpened():
            self.logger.error("Failed to open video source")
            return False
        
        # Get video properties for output
        w, h = self.video_reader.get_resolution()
        fps = self.video_reader.get_frame_rate()
        self.total_frames = self.video_reader.get_total_frames()
        
        # Initialize video writer
        output_path = self._resolve_path(self.config.get('output_video', 'output/processed_video.mp4'))
        self.video_writer = VideoWriter(output_path, w, h, fps)
        
        # Initialize preprocessor
        self.preprocessor = ImagePreprocessor(
            canny_low=self.config.get('canny_low_threshold', 50),
            canny_high=self.config.get('canny_high_threshold', 150),
            gaussian_kernel=self._normalize_kernel(self.config.get('gaussian_blur_kernel', (5, 5))),
            roi_top_percent=self.config.get('roi_top_percent', 0.4),
            roi_bottom_percent=self.config.get('roi_bottom_percent', 1.0)
        )
        
        # Initialize lane detector
        self.lane_detector = LaneDetector(
            hough_rho=self.config.get('hough_rho', 2),
            hough_theta=self.config.get('hough_theta', 1),
            hough_threshold=self.config.get('hough_threshold', 30),
            hough_min_line_length=self.config.get('hough_min_line_length', 50),
            hough_max_line_gap=self.config.get('hough_max_line_gap', 20),
            history_buffer_size=self.config.get('history_buffer_size', 5)
        )
        
        # Initialize curvature calculator
        self.curvature_calculator = CurvatureCalculator(
            poly_degree=self.config.get('poly_degree', 2)
        )
        
        # Initialize position estimator
        self.position_estimator = PositionEstimator()
        
        # Initialize warning system
        self.lane_warning = LaneWarning(
            departure_threshold=self.config.get('departure_threshold', 0.3)
        )
        
        self.logger.info("All components initialized successfully")
        return True
    
    def process_frame(self, frame):
        """
        Process single frame through pipeline
        
        Args:
            frame: Input frame
            
        Returns:
            Processed frame with visualizations
        """
        self.frame_count += 1
        self.fps_counter.update()
        
        # Create copy for visualization
        vis_frame = frame.copy()
        
        # Apply gamma correction for night mode if enabled
        if self.config.get('enable_night_mode', False):
            frame = self.preprocessor.apply_night_mode(
                frame, 
                gamma=self.config.get('night_gamma_correction', 1.5)
            )
        
        # Preprocessing
        preprocessed = self.preprocessor.preprocess(frame)
        
        # Try color-based detection as well
        if self.config.get('use_adaptive_threshold', False):
            color_detected = self.preprocessor.preprocess_with_color_detection(frame)
            preprocessed = cv2.bitwise_or(preprocessed, color_detected)
        
        # Lane detection
        left_lane, right_lane = self.lane_detector.detect_lanes(preprocessed)
        
        # Draw lane overlay
        if left_lane or right_lane:
            DrawingUtils.draw_lane_overlay(vis_frame, left_lane, right_lane,
                                          color=tuple(self.config.get('lane_color', [0, 255, 0])))
            DrawingUtils.draw_lane_fill(vis_frame, left_lane, right_lane, alpha=0.2)
        
        # Curvature estimation
        curvature_info = self.curvature_calculator.calculate_curvature(left_lane, right_lane)
        
        # Vehicle position estimation
        position_info = self.position_estimator.estimate_position(
            vis_frame, left_lane, right_lane
        )
        
        # Draw vehicle center and lane center
        if position_info['lane_center_x'] is not None:
            vehicle_x, vehicle_y = self.position_estimator.get_vehicle_center_coordinates()
            lane_center_x = position_info['lane_center_x']
            
            # Draw center line reference
            cv2.line(vis_frame, (lane_center_x, int(vehicle_y - 100)),
                    (lane_center_x, int(vehicle_y + 20)),
                    tuple(self.config.get('center_line_color', [255, 255, 0])), 2)
            
            # Draw vehicle position marker
            DrawingUtils.draw_circle(vis_frame, (vehicle_x, vehicle_y), 5,
                                    color=(0, 255, 0), thickness=-1)
        
        # Lane departure warning
        warning_info = self.lane_warning.update(position_info)
        
        # Draw warnings
        self._draw_warnings(vis_frame, warning_info, curvature_info, position_info)
        
        # Draw information overlay
        self._draw_info_overlay(vis_frame, position_info, curvature_info, warning_info)
        
        return vis_frame
    
    def _draw_warnings(self, frame, warning_info, curvature_info, position_info):
        """
        Draw warning visualizations on frame
        
        Args:
            frame: Frame to draw on
            warning_info: Warning information
            curvature_info: Curvature information
            position_info: Position information
        """
        h, w = frame.shape[:2]
        
        # Lane departure warning
        if warning_info['warning_active']:
            warning_color = tuple(self.config.get('warning_color', [0, 0, 255]))
            
            # Draw red border for critical warnings
            cv2.rectangle(frame, (0, 0), (w, h), warning_color, 5)
            
            # Draw warning text in center
            font_scale = self.config.get('warning_font_scale', 0.8)
            DrawingUtils.draw_centered_text(frame, warning_info['warning_message'],
                                           color=warning_color, font_scale=font_scale + 0.5)
        
        # Curvature warning
        curve_warning = self.lane_warning.check_road_curvature_warning(curvature_info)
        if curve_warning['warning_active']:
            DrawingUtils.draw_text(frame, curve_warning['warning_message'],
                                  (20, 100), color=(0, 165, 255), font_scale=0.7)
    
    def _draw_info_overlay(self, frame, position_info, curvature_info, warning_info):
        """
        Draw information overlay on frame
        
        Args:
            frame: Frame to draw on
            position_info: Position information
            curvature_info: Curvature information
            warning_info: Warning information
        """
        h, w = frame.shape[:2]
        
        # FPS counter
        if self.config.get('display_fps', True):
            fps = self.fps_counter.get_fps()
            DrawingUtils.draw_text(frame, f"FPS: {fps:.1f}", (10, 30),
                                  color=(0, 255, 0), font_scale=0.6)
        
        # Frame counter
        DrawingUtils.draw_text(frame, f"Frame: {self.frame_count}/{self.total_frames}",
                              (10, 60), color=(200, 200, 200), font_scale=0.5)
        
        # Lane offset
        if self.config.get('display_offset', True) and position_info['offset_meters'] is not None:
            offset_m = position_info['offset_meters']
            offset_label = f"Offset: {offset_m:+.2f}m"
            DrawingUtils.draw_text(frame, offset_label, (10, 90),
                                  color=(255, 200, 0), font_scale=0.6)
        
        # Position in lane
        if position_info['position_in_lane'] is not None:
            pos_label = f"Position: {position_info['position_in_lane']}"
            DrawingUtils.draw_text(frame, pos_label, (10, 120),
                                  color=(200, 255, 0), font_scale=0.6)
        
        # Curvature
        if self.config.get('display_curvature', True) and curvature_info['average_curvature'] is not None:
            curv = curvature_info['average_curvature']
            curv_label = f"Curvature: {curv:.0f}px"
            road_type = self.curvature_calculator.classify_road_type(curv)
            DrawingUtils.draw_text(frame, curv_label, (10, 150),
                                  color=(100, 200, 255), font_scale=0.6)
            DrawingUtils.draw_text(frame, f"Road: {road_type}", (10, 180),
                                  color=(100, 200, 255), font_scale=0.6)
        
        # Warning status
        if self.config.get('display_warning', True):
            if warning_info['warning_active']:
                DrawingUtils.draw_text(frame, "ALERT ACTIVE", (10, 210),
                                      color=(0, 0, 255), font_scale=0.7, thickness=2)
        
        # Helper text at bottom
        DrawingUtils.draw_text(frame, "Press 'q' to quit | 'p' to pause", (10, h-20),
                              color=(150, 150, 150), font_scale=0.5)
    
    def run(self):
        """Run the lane detection system"""
        
        if not self.initialize_components():
            self.logger.error("Failed to initialize components")
            return
        
        self.logger.info("Starting video processing...")
        
        pause = False
        
        while True:
            if not pause:
                ret, frame = self.video_reader.read_frame()
                
                if not ret:
                    self.logger.info("End of video reached")
                    break
                
                # Process frame
                processed_frame = self.process_frame(frame)
                
                # Write to output
                self.video_writer.write_frame(processed_frame)
            else:
                processed_frame = frame
            
            # Display frame
            cv2.imshow(self.window_name, processed_frame)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                self.logger.info("User quit requested")
                break
            elif key == ord('p'):
                pause = not pause
                state = "PAUSED" if pause else "PLAYING"
                self.logger.info(f"Video {state}")
        
        self._cleanup()
    
    def _cleanup(self):
        """Cleanup and release resources"""
        self.logger.info("Cleaning up resources...")
        
        if self.video_reader:
            self.video_reader.release()
        
        if self.video_writer:
            self.video_writer.release()
        
        cv2.destroyAllWindows()
        
        # Log statistics
        self.logger.info("=" * 70)
        self.logger.info("SYSTEM STATISTICS")
        self.logger.info("=" * 70)
        self.logger.info(f"Total frames processed: {self.frame_count}")
        self.logger.info(f"Average FPS: {self.fps_counter.get_fps():.2f}")
        self.logger.info(f"Total elapsed time: {self.fps_counter.get_elapsed_time():.2f}s")
        self.logger.info(f"Lane detector stats: {self.lane_detector.get_statistics()}")
        self.logger.info(f"Warning system stats: {self.lane_warning.get_statistics()}")
        self.logger.info("=" * 70)


def main():
    """Main entry point"""
    try:
        system = LaneDetectionSystem(config_path='config/config.yaml')
        system.run()
    except Exception as e:
        SystemLogger().error(f"Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
