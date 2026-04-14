"""Video Reader module for loading and processing video files"""

import cv2
import os
from utils.logger import SystemLogger


class VideoReader:
    """Handles video input from files or camera"""
    
    def __init__(self, video_source):
        """
        Initialize video reader
        
        Args:
            video_source: Path to video file or camera index (0 for default camera)
        """
        self.logger = SystemLogger().get_logger()
        self.video_source = video_source
        self.cap = None
        self.frame_width = 0
        self.frame_height = 0
        self.fps = 0
        self.total_frames = 0
        self.current_frame_idx = 0
        self.is_camera = isinstance(video_source, int)
        
        self._initialize()
    
    def _initialize(self):
        """Initialize video capture"""
        try:
            if self.is_camera:
                self.cap = cv2.VideoCapture(self.video_source)
                self.logger.info(f"Camera initialized (index: {self.video_source})")
            else:
                if not os.path.exists(self.video_source):
                    self.logger.error(f"Video file not found: {self.video_source}")
                    return False
                
                self.cap = cv2.VideoCapture(self.video_source)
                self.logger.info(f"Video loaded: {self.video_source}")
            
            if not self.cap.isOpened():
                self.logger.error("Failed to open video source")
                return False
            
            # Get video properties
            self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.fps = self.cap.get(cv2.CAP_PROP_FPS)
            
            if not self.is_camera:
                self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            self.logger.info(f"Video properties: {self.frame_width}x{self.frame_height} @ {self.fps} FPS")
            return True
        
        except Exception as e:
            self.logger.error(f"Error initializing video: {str(e)}")
            return False
    
    def read_frame(self):
        """
        Read next frame from video
        
        Returns:
            tuple: (success, frame)
        """
        if self.cap is None:
            return False, None
        
        ret, frame = self.cap.read()
        
        if ret:
            self.current_frame_idx += 1
        
        return ret, frame
    
    def get_frame_rate(self):
        """Get video frames per second"""
        return self.fps
    
    def get_resolution(self):
        """Get video resolution (width, height)"""
        return (self.frame_width, self.frame_height)
    
    def get_total_frames(self):
        """Get total number of frames"""
        return self.total_frames
    
    def get_current_frame_idx(self):
        """Get current frame index"""
        return self.current_frame_idx
    
    def set_frame_position(self, frame_idx):
        """
        Set video to specific frame
        
        Args:
            frame_idx: Frame index to seek to
        """
        if self.cap is not None and not self.is_camera:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            self.current_frame_idx = frame_idx
    
    def reset(self):
        """Reset video to beginning"""
        if self.cap is not None and not self.is_camera:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self.current_frame_idx = 0
    
    def release(self):
        """Release video capture"""
        if self.cap is not None:
            self.cap.release()
            self.logger.info("Video reader released")
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        self.release()


class VideoWriter:
    """Handles video output to file"""
    
    def __init__(self, output_path, frame_width, frame_height, fps=30.0):
        """
        Initialize video writer
        
        Args:
            output_path: Path to output video file
            frame_width: Video width
            frame_height: Video height
            fps: Frames per second
        """
        self.logger = SystemLogger().get_logger()
        self.output_path = output_path
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.fps = fps
        
        # Create output directory if needed
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        
        # Define codec and create VideoWriter
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.writer = cv2.VideoWriter(output_path, fourcc, fps, 
                                      (frame_width, frame_height))
        
        if self.writer.isOpened():
            self.logger.info(f"Video writer initialized: {output_path}")
        else:
            self.logger.error(f"Failed to initialize video writer: {output_path}")
    
    def write_frame(self, frame):
        """
        Write frame to video
        
        Args:
            frame: Frame to write
            
        Returns:
            bool: Success status
        """
        if self.writer is None:
            return False
        
        try:
            self.writer.write(frame)
            return True
        except Exception as e:
            self.logger.error(f"Error writing frame: {str(e)}")
            return False
    
    def release(self):
        """Release video writer"""
        if self.writer is not None:
            self.writer.release()
            self.logger.info(f"Video saved: {self.output_path}")
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        self.release()
