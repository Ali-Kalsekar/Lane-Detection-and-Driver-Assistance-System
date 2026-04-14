"""Image preprocessing module for lane detection"""

import cv2
import numpy as np
from utils.logger import SystemLogger


class ImagePreprocessor:
    """Handles image preprocessing for lane detection"""
    
    def __init__(self, canny_low=50, canny_high=150, 
                 gaussian_kernel=(5, 5), roi_top_percent=0.4, 
                 roi_bottom_percent=1.0, use_adaptive=False):
        """
        Initialize image preprocessor
        
        Args:
            canny_low: Canny edge detection low threshold
            canny_high: Canny edge detection high threshold
            gaussian_kernel: Gaussian blur kernel size
            roi_top_percent: Region of interest top percentage
            roi_bottom_percent: Region of interest bottom percentage
            use_adaptive: Use adaptive thresholding
        """
        self.logger = SystemLogger().get_logger()
        self.canny_low = canny_low
        self.canny_high = canny_high
        self.gaussian_kernel = gaussian_kernel
        self.roi_top_percent = roi_top_percent
        self.roi_bottom_percent = roi_bottom_percent
        self.use_adaptive = use_adaptive
        self.image_height = 0
        self.image_width = 0
    
    def preprocess(self, image):
        """
        Complete preprocessing pipeline
        
        Args:
            image: Input image
            
        Returns:
            Preprocessed image
        """
        self.image_height, self.image_width = image.shape[:2]
        
        # Convert to grayscale
        gray = self._to_grayscale(image)
        
        # Apply Gaussian blur
        blurred = self._gaussian_blur(gray)
        
        # Apply edge detection
        edges = self._canny_edge_detection(blurred)
        
        # Apply region of interest mask
        masked = self._apply_roi_mask(edges)
        
        return masked
    
    def preprocess_with_color_detection(self, image):
        """
        Preprocessing with color lane detection
        
        Args:
            image: Input image
            
        Returns:
            Color-detected lanes
        """
        # Convert to HSV for better color detection
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Define color ranges for white and yellow lanes
        lower_white = np.array([0, 0, 200])
        upper_white = np.array([180, 30, 255])
        
        lower_yellow = np.array([15, 100, 100])
        upper_yellow = np.array([35, 255, 255])
        
        # Create masks
        white_mask = cv2.inRange(hsv, lower_white, upper_white)
        yellow_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
        
        # Combine masks
        combined_mask = cv2.bitwise_or(white_mask, yellow_mask)
        
        # Apply morphological operations
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel)
        combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel)
        
        # Apply ROI mask
        masked = self._apply_roi_mask(combined_mask)
        
        return masked
    
    def apply_night_mode(self, image, gamma=1.5):
        """
        Apply gamma correction for night driving
        
        Args:
            image: Input image
            gamma: Gamma correction factor
            
        Returns:
            Gamma corrected image
        """
        # Build lookup table for gamma correction
        inv_gamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** inv_gamma) * 255 
                         for i in np.arange(0, 256)]).astype("uint8")
        
        # Apply gamma correction
        return cv2.LUT(image, table)
    
    def _to_grayscale(self, image):
        """
        Convert image to grayscale
        
        Args:
            image: Input image
            
        Returns:
            Grayscale image
        """
        if len(image.shape) == 3:
            return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return image
    
    def _gaussian_blur(self, image):
        """
        Apply Gaussian blur
        
        Args:
            image: Input image
            
        Returns:
            Blurred image
        """
        return cv2.GaussianBlur(image, self.gaussian_kernel, 0)
    
    def _canny_edge_detection(self, image):
        """
        Apply Canny edge detection
        
        Args:
            image: Input image
            
        Returns:
            Edge-detected image
        """
        edges = cv2.Canny(image, self.canny_low, self.canny_high)
        
        # Dilate edges for better connectivity
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        edges = cv2.dilate(edges, kernel, iterations=1)
        
        return edges
    
    def _apply_adaptive_threshold(self, image):
        """
        Apply adaptive thresholding
        
        Args:
            image: Input image
            
        Returns:
            Thresholded image
        """
        binary = cv2.adaptiveThreshold(image, 255,
                                       cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY, 11, 2)
        return binary
    
    def _apply_roi_mask(self, image):
        """
        Apply region of interest mask
        
        Args:
            image: Input image
            
        Returns:
            Masked image
        """
        h, w = image.shape[:2]
        
        # Define ROI vertices
        top_y = int(h * self.roi_top_percent)
        bottom_y = int(h * self.roi_bottom_percent)
        
        # Create mask
        mask = np.zeros_like(image)
        
        # Define region (trapezoid for perspective)
        vertices = np.array([
            [0, bottom_y],
            [int(w * 0.1), top_y],
            [int(w * 0.9), top_y],
            [w, bottom_y]
        ], dtype=np.int32)
        
        cv2.fillPoly(mask, [vertices], 255)
        
        # Apply mask
        return cv2.bitwise_and(image, mask)
    
    def apply_perspective_transform(self, image):
        """
        Apply perspective transform for bird's eye view
        
        Args:
            image: Input image
            
        Returns:
            Transformed image and transformation matrix
        """
        h, w = image.shape[:2]
        
        # Define source points (current view)
        src_points = np.float32([
            [0, h],
            [0, int(h * 0.6)],
            [w, int(h * 0.6)],
            [w, h]
        ])
        
        # Define destination points (bird's eye view)
        dst_points = np.float32([
            [int(w * 0.3), h],
            [int(w * 0.3), 0],
            [int(w * 0.7), 0],
            [int(w * 0.7), h]
        ])
        
        # Get perspective transform matrix
        matrix = cv2.getPerspectiveTransform(src_points, dst_points)
        
        # Warp perspective
        warped = cv2.warpPerspective(image, matrix, (w, h))
        
        return warped, matrix
    
    def get_roi_vertices(self):
        """
        Get ROI vertices for visualization
        
        Returns:
            Array of vertices
        """
        h, w = self.image_height, self.image_width
        top_y = int(h * self.roi_top_percent)
        bottom_y = int(h * self.roi_bottom_percent)
        
        vertices = np.array([
            [0, bottom_y],
            [int(w * 0.1), top_y],
            [int(w * 0.9), top_y],
            [w, bottom_y]
        ], dtype=np.int32)
        
        return vertices
