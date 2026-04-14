"""Vehicle position estimation module"""

import numpy as np
from utils.logger import SystemLogger


class PositionEstimator:
    """Estimates vehicle position relative to lanes"""
    
    def __init__(self, pixels_per_meter=3.7/700, vehicle_center_y_percent=0.95):
        """
        Initialize position estimator
        
        Args:
            pixels_per_meter: Pixel to meter conversion factor
            vehicle_center_y_percent: Y position of vehicle center as percent of image height
        """
        self.logger = SystemLogger().get_logger()
        self.pixels_per_meter = pixels_per_meter
        self.vehicle_center_y_percent = vehicle_center_y_percent
        self.image_height = 0
        self.image_width = 0
    
    def estimate_position(self, image, left_lane, right_lane):
        """
        Estimate vehicle position relative to lanes
        
        Args:
            image: Input image
            left_lane: Left lane points
            right_lane: Right lane points
            
        Returns:
            dict: Position information
        """
        self.image_height, self.image_width = image.shape[:2]
        
        result = {
            'vehicle_x': None,
            'lane_center_x': None,
            'offset_pixels': None,
            'offset_meters': None,
            'offset_normalized': None,
            'position_in_lane': None,  # 'CENTER', 'LEFT', 'RIGHT'
            'lane_width': None
        }
        
        # Get vehicle center position
        vehicle_x = self._get_vehicle_center_x()
        result['vehicle_x'] = vehicle_x
        
        # Get lane center position
        if left_lane and right_lane:
            lane_center_x = self._get_lane_center(left_lane, right_lane)
            result['lane_center_x'] = lane_center_x
            
            # Calculate offset
            if lane_center_x is not None:
                offset_pixels = vehicle_x - lane_center_x
                result['offset_pixels'] = offset_pixels
                result['offset_meters'] = offset_pixels * self.pixels_per_meter
                
                # Normalized offset (-1 to 1)
                lane_width = self._get_lane_width(left_lane, right_lane)
                result['lane_width'] = lane_width
                
                if lane_width > 0:
                    result['offset_normalized'] = offset_pixels / (lane_width / 2)
                
                # Determine position
                result['position_in_lane'] = self._classify_position(offset_pixels, lane_width)
        
        return result
    
    def _get_vehicle_center_x(self):
        """
        Get vehicle center X coordinate
        
        Returns:
            int: Vehicle center X position
        """
        return self.image_width // 2
    
    def _get_vehicle_center_y(self):
        """
        Get vehicle center Y coordinate (bottom of image)
        
        Returns:
            int: Vehicle center Y position
        """
        return int(self.image_height * self.vehicle_center_y_percent)
    
    def _get_lane_center(self, left_lane, right_lane):
        """
        Get lane center position at vehicle center Y
        
        Args:
            left_lane: Left lane points
            right_lane: Right lane points
            
        Returns:
            int: Lane center X position
        """
        vehicle_y = self._get_vehicle_center_y()
        
        # Find left lane point closest to vehicle_y
        left_x = None
        min_left_diff = float('inf')
        for x, y in left_lane:
            diff = abs(y - vehicle_y)
            if diff < min_left_diff:
                min_left_diff = diff
                left_x = x
        
        # Find right lane point closest to vehicle_y
        right_x = None
        min_right_diff = float('inf')
        for x, y in right_lane:
            diff = abs(y - vehicle_y)
            if diff < min_right_diff:
                min_right_diff = diff
                right_x = x
        
        if left_x is not None and right_x is not None:
            return (left_x + right_x) // 2
        
        return None
    
    def _get_lane_width(self, left_lane, right_lane):
        """
        Get lane width at vehicle position
        
        Args:
            left_lane: Left lane points
            right_lane: Right lane points
            
        Returns:
            int: Lane width in pixels
        """
        vehicle_y = self._get_vehicle_center_y()
        
        left_x = None
        right_x = None
        
        # Find closest points at vehicle Y level
        min_left_diff = float('inf')
        for x, y in left_lane:
            diff = abs(y - vehicle_y)
            if diff < min_left_diff:
                min_left_diff = diff
                left_x = x
        
        min_right_diff = float('inf')
        for x, y in right_lane:
            diff = abs(y - vehicle_y)
            if diff < min_right_diff:
                min_right_diff = diff
                right_x = x
        
        if left_x is not None and right_x is not None:
            return abs(right_x - left_x)
        
        return 0
    
    def _classify_position(self, offset_pixels, lane_width):
        """
        Classify vehicle position in lane
        
        Args:
            offset_pixels: Offset from lane center in pixels
            lane_width: Lane width in pixels
            
        Returns:
            str: Position classification
        """
        if lane_width == 0:
            return "UNKNOWN"
        
        threshold = lane_width / 4  # Quarter lane width threshold
        
        if abs(offset_pixels) < threshold:
            return "CENTER"
        elif offset_pixels < -threshold:
            return "LEFT"
        else:
            return "RIGHT"
    
    def get_vehicle_center_coordinates(self):
        """
        Get vehicle center coordinates
        
        Returns:
            tuple: (x, y) coordinates
        """
        return (self._get_vehicle_center_x(), self._get_vehicle_center_y())
    
    def calculate_steering_angle(self, offset_pixels):
        """
        Estimate steering angle needed based on offset
        
        Args:
            offset_pixels: Vehicle offset from lane center
            
        Returns:
            float: Steering angle in degrees (positive = right, negative = left)
        """
        # Simple proportional steering (can be improved with PID)
        # Normalize to -30 to +30 degrees based on typical image width
        max_offset = self.image_width / 2
        max_angle = 30
        
        angle = (offset_pixels / max_offset) * max_angle
        return np.clip(angle, -max_angle, max_angle)
    
    def reset(self):
        """Reset estimator"""
        self.image_height = 0
        self.image_width = 0
