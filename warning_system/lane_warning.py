"""Lane departure warning system"""

from utils.logger import SystemLogger


class LaneWarning:
    """Detects lane departure and generates warnings"""
    
    def __init__(self, departure_threshold=0.3, warning_cooldown=30):
        """
        Initialize lane warning system
        
        Args:
            departure_threshold: Normalized offset threshold for warning (0-1)
            warning_cooldown: Frames before warning can be triggered again
        """
        self.logger = SystemLogger().get_logger()
        self.departure_threshold = departure_threshold
        self.warning_cooldown = warning_cooldown
        self.cooldown_counter = 0
        self.last_warning_frame = -warning_cooldown
        self.warning_active = False
        self.warning_message = ""
        self.frame_count = 0
    
    def update(self, position_info):
        """
        Update warning system with position information
        
        Args:
            position_info: Dictionary with position data
            
        Returns:
            dict: Warning information
        """
        self.frame_count += 1
        self.cooldown_counter += 1
        
        warning_result = {
            'warning_active': False,
            'warning_type': None,
            'warning_message': "",
            'severity': None,  # 'LOW', 'MEDIUM', 'HIGH'
            'position_info': position_info
        }
        
        # Check if lanes were detected
        if position_info['lane_center_x'] is None:
            warning_result['warning_message'] = "WARNING: Lane Detection Failed"
            warning_result['warning_type'] = 'DETECTION_FAILED'
            warning_result['severity'] = 'MEDIUM'
            warning_result['warning_active'] = True
            return warning_result
        
        # Check lane departure
        offset_normalized = position_info['offset_normalized']
        
        if offset_normalized is not None:
            if abs(offset_normalized) > self.departure_threshold:
                # Generate warning if cooldown has elapsed
                if self.cooldown_counter > self.warning_cooldown:
                    warning_result['warning_active'] = True
                    self.warning_active = True
                    self.cooldown_counter = 0
                    self.last_warning_frame = self.frame_count
                    
                    # Determine warning type and message
                    if offset_normalized < -self.departure_threshold:
                        warning_result['warning_type'] = 'LEFT_DEPARTURE'
                        warning_result['warning_message'] = "⚠ WARNING: Drifting LEFT"
                        warning_result['severity'] = 'HIGH'
                    else:
                        warning_result['warning_type'] = 'RIGHT_DEPARTURE'
                        warning_result['warning_message'] = "⚠ WARNING: Drifting RIGHT"
                        warning_result['severity'] = 'HIGH'
                else:
                    # Still in warning period but cooldown active
                    if self.warning_active:
                        warning_result['warning_active'] = True
                        warning_result['warning_message'] = (
                            "⚠ WARNING: Lane Departure Detected"
                        )
                        warning_result['severity'] = 'HIGH'
            else:
                # Not departing lane
                self.warning_active = False
        
        return warning_result
    
    def check_road_curvature_warning(self, curvature_info):
        """
        Generate warnings based on road curvature
        
        Args:
            curvature_info: Curvature information dictionary
            
        Returns:
            dict: Curvature warning information
        """
        warning_result = {
            'warning_active': False,
            'warning_message': "",
            'road_type': None,
            'severity': None
        }
        
        if curvature_info['average_curvature'] is None:
            return warning_result
        
        curv = curvature_info['average_curvature']
        
        # Determine road type and generate warnings
        if curv < 300:
            warning_result['road_type'] = 'TIGHT_CURVE'
            warning_result['warning_message'] = "⚠ Tight Curve Ahead - Reduce Speed"
            warning_result['severity'] = 'HIGH'
            warning_result['warning_active'] = True
        elif curv < 800:
            warning_result['road_type'] = 'MODERATE_CURVE'
            warning_result['warning_message'] = "⚠ Moderate Curve Detected"
            warning_result['severity'] = 'MEDIUM'
            warning_result['warning_active'] = True
        elif curv < 2000:
            warning_result['road_type'] = 'GENTLE_CURVE'
            warning_result['warning_message'] = "Gentle Curve"
            warning_result['severity'] = 'LOW'
        else:
            warning_result['road_type'] = 'STRAIGHT'
        
        return warning_result
    
    def reset(self):
        """Reset warning system"""
        self.cooldown_counter = 0
        self.warning_active = False
        self.warning_message = ""
        self.frame_count = 0
    
    def get_statistics(self):
        """Get warning statistics"""
        return {
            'total_frames_processed': self.frame_count,
            'warning_active': self.warning_active,
            'frames_since_last_warning': self.frame_count - self.last_warning_frame
        }
