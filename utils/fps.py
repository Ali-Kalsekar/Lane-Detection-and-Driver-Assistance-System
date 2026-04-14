"""FPS Counter utility module"""

import time


class FPSCounter:
    """Real-time FPS counter for video processing"""
    
    def __init__(self, window_size=30):
        """
        Initialize FPS counter
        
        Args:
            window_size: Number of frames to average over
        """
        self.window_size = window_size
        self.frame_times = []
        self.start_time = time.time()
        self.frame_count = 0
    
    def update(self):
        """Update FPS counter with new frame"""
        current_time = time.time()
        
        if len(self.frame_times) > 0:
            elapsed = current_time - self.frame_times[-1]
            self.frame_times.append(elapsed)
        else:
            self.frame_times.append(0)
        
        # Keep only recent frames in buffer
        if len(self.frame_times) > self.window_size:
            self.frame_times.pop(0)
        
        self.frame_count += 1
    
    def get_fps(self):
        """
        Calculate and return current FPS
        
        Returns:
            float: Frames per second
        """
        if len(self.frame_times) < 2:
            return 0.0
        
        # Calculate average frame time (excluding first zero)
        total_time = sum(self.frame_times[1:])
        count = len(self.frame_times) - 1
        
        if total_time == 0:
            return 0.0
        
        avg_time = total_time / count
        return 1.0 / avg_time if avg_time > 0 else 0.0
    
    def get_frame_count(self):
        """Get total frames processed"""
        return self.frame_count
    
    def reset(self):
        """Reset counter"""
        self.frame_times = []
        self.frame_count = 0
        self.start_time = time.time()
    
    def get_elapsed_time(self):
        """Get elapsed time since start"""
        return time.time() - self.start_time
