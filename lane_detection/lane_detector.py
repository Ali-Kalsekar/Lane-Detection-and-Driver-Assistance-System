"""Lane detection module using Hough Transform"""

import cv2
import numpy as np
from collections import deque
from utils.logger import SystemLogger


class LaneDetector:
    """Detects and tracks lane lines using Hough Transform"""
    
    def __init__(self, hough_rho=2, hough_theta=1, hough_threshold=30,
                 hough_min_line_length=50, hough_max_line_gap=20,
                 history_buffer_size=5):
        """
        Initialize lane detector
        
        Args:
            hough_rho: Distance resolution of Hough accumulator
            hough_theta: Angle resolution of Hough accumulator (in degrees)
            hough_threshold: Accumulator threshold
            hough_min_line_length: Minimum line length
            hough_max_line_gap: Maximum line gap
            history_buffer_size: Number of frames to keep for smoothing
        """
        self.logger = SystemLogger().get_logger()
        self.hough_rho = hough_rho
        self.hough_theta = np.pi / 180 * hough_theta
        self.hough_threshold = hough_threshold
        self.hough_min_line_length = hough_min_line_length
        self.hough_max_line_gap = hough_max_line_gap
        self.history_buffer_size = history_buffer_size
        
        # History buffers for lane smoothing
        self.left_lane_history = deque(maxlen=history_buffer_size)
        self.right_lane_history = deque(maxlen=history_buffer_size)
        
        # Store last detected lanes
        self.last_left_lane = None
        self.last_right_lane = None
        self.frame_count = 0
    
    def detect_lanes(self, image):
        """
        Detect lane lines in image
        
        Args:
            image: Preprocessed image (binary/edge image)
            
        Returns:
            tuple: (left_lane, right_lane) as lists of (x, y) points
        """
        self.frame_count += 1
        
        # Detect lines using Hough Transform
        lines = cv2.HoughLinesP(image, self.hough_rho, self.hough_theta,
                               self.hough_threshold, self.hough_min_line_length,
                               self.hough_max_line_gap)
        
        if lines is None:
            # Return smoothed previous lanes if tracking fails
            return self._get_smoothed_lanes()
        
        # Separate lines into left and right lanes
        left_lines, right_lines = self._separate_lanes(lines, image)
        
        # Convert lines to lane curves
        left_lane = self._lines_to_lane(left_lines, image)
        right_lane = self._lines_to_lane(right_lines, image)
        
        # Smooth lanes using history
        left_lane = self._smooth_lane(left_lane, self.left_lane_history)
        right_lane = self._smooth_lane(right_lane, self.right_lane_history)
        
        # Update last detected lanes
        if left_lane is not None and len(left_lane) > 0:
            self.last_left_lane = left_lane
        if right_lane is not None and len(right_lane) > 0:
            self.last_right_lane = right_lane
        
        return left_lane, right_lane
    
    def _separate_lanes(self, lines, image):
        """
        Separate detected lines into left and right lanes
        
        Args:
            lines: Detected lines from Hough transform
            image: Original image for getting width
            
        Returns:
            tuple: (left_lines, right_lines)
        """
        left_lines = []
        right_lines = []
        
        if lines is None or len(lines) == 0:
            return left_lines, right_lines
        
        h, w = image.shape[:2]
        center_x = w / 2
        
        for line in lines:
            x1, y1, x2, y2 = line[0]
            
            # Calculate slope
            if x2 - x1 == 0:  # Vertical line
                continue
            
            slope = (y2 - y1) / (x2 - x1)
            
            # Filter by reasonable slope (avoid near-horizontal and near-vertical)
            if abs(slope) < 0.3 or abs(slope) > 3:
                continue
            
            # Separate by x position relative to center
            mid_x = (x1 + x2) / 2
            
            if mid_x < center_x and slope < 0:  # Left lane (negative slope)
                left_lines.append(line[0])
            elif mid_x > center_x and slope > 0:  # Right lane (positive slope)
                right_lines.append(line[0])
        
        return left_lines, right_lines
    
    def _lines_to_lane(self, lines, image):
        """
        Convert detected lines to continuous lane curve
        
        Args:
            lines: List of detected lines
            image: Original image
            
        Returns:
            list: Lane points as (x, y) tuples
        """
        if not lines or len(lines) == 0:
            return None
        
        h, w = image.shape[:2]
        
        # Extract endpoints
        points = []
        for line in lines:
            x1, y1, x2, y2 = line
            points.extend([(x1, y1), (x2, y2)])
        
        points = np.array(points, dtype=np.float32)
        
        # Fit a line to points using least squares
        vx, vy, x0, y0 = cv2.fitLine(points, cv2.DIST_L2, 0, 0.01, 0.01)
        
        # Generate lane curve from top to bottom of ROI
        lane_points = []
        for y in range(0, h, 5):
            if vy != 0:
                x = int(x0 + vx * (y - y0) / vy)
                # Keep points within image bounds
                if 0 <= x < w:
                    lane_points.append((x, y))
        
        return lane_points if lane_points else None
    
    def _smooth_lane(self, lane, history_buffer):
        """
        Smooth lane using history buffer
        
        Args:
            lane: Current detected lane
            history_buffer: Deque storing previous lanes
            
        Returns:
            Smoothed lane
        """
        if lane is None:
            # Use average from history if current detection fails
            if len(history_buffer) > 0:
                return self._average_lanes(list(history_buffer))
            return None
        
        # Add current lane to history
        history_buffer.append(lane)
        
        # If we have enough history, smooth
        if len(history_buffer) >= 2:
            return self._average_lanes(list(history_buffer))
        
        return lane
    
    def _average_lanes(self, lane_list):
        """
        Average multiple lanes for smoothing
        
        Args:
            lane_list: List of lane point lists
            
        Returns:
            Averaged lane
        """
        if not lane_list or len(lane_list[0]) == 0:
            return None
        
        # Get common y values
        all_y = set()
        for lane in lane_list:
            all_y.update([p[1] for p in lane])
        
        all_y = sorted(all_y)
        averaged_lane = []
        
        for y in all_y:
            x_values = []
            for lane in lane_list:
                for x, py in lane:
                    if abs(py - y) < 5:  # Find points close to y
                        x_values.append(x)
                        break
            
            if x_values:
                avg_x = int(np.mean(x_values))
                averaged_lane.append((avg_x, y))
        
        return averaged_lane if averaged_lane else None
    
    def _get_smoothed_lanes(self):
        """Get last smoothed lanes when detection fails"""
        return self.last_left_lane, self.last_right_lane
    
    def reset(self):
        """Reset lane detector"""
        self.left_lane_history.clear()
        self.right_lane_history.clear()
        self.last_left_lane = None
        self.last_right_lane = None
        self.frame_count = 0
    
    def get_statistics(self):
        """Get detection statistics"""
        return {
            'frames_processed': self.frame_count,
            'history_buffer_size': self.history_buffer_size,
            'left_lane_available': self.last_left_lane is not None,
            'right_lane_available': self.last_right_lane is not None
        }
