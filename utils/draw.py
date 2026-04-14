"""Drawing utilities for visualization overlays"""

import cv2
import numpy as np


class DrawingUtils:
    """Utility functions for drawing overlays on frames"""
    
    @staticmethod
    def draw_lane_overlay(image, left_lane, right_lane, color=(0, 255, 0), thickness=3):
        """
        Draw lane lines on image
        
        Args:
            image: Input image
            left_lane: Left lane points
            right_lane: Right lane points
            color: BGR color tuple
            thickness: Line thickness
        """
        if left_lane is not None and len(left_lane) > 1:
            left_lane = np.array(left_lane, dtype=np.int32)
            cv2.polylines(image, [left_lane], False, color, thickness)
        
        if right_lane is not None and len(right_lane) > 1:
            right_lane = np.array(right_lane, dtype=np.int32)
            cv2.polylines(image, [right_lane], False, color, thickness)
    
    @staticmethod
    def draw_lane_fill(image, left_lane, right_lane, alpha=0.3):
        """
        Draw filled lane area between lines
        
        Args:
            image: Input image
            left_lane: Left lane points
            right_lane: Right lane points
            alpha: Transparency factor
        """
        if left_lane is None or right_lane is None:
            return
        
        if len(left_lane) < 2 or len(right_lane) < 2:
            return
        
        # Create lane polygon
        left_lane = np.array(left_lane, dtype=np.int32)
        right_lane = np.array(right_lane, dtype=np.int32)
        
        # Reverse right lane to create closed polygon
        right_lane_reversed = right_lane[::-1]
        
        # Combine points
        lane_points = np.vstack((left_lane, right_lane_reversed))
        
        # Create overlay
        overlay = image.copy()
        cv2.fillPoly(overlay, [lane_points], (0, 255, 0))
        
        # Blend
        cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0, image)
    
    @staticmethod
    def draw_text(image, text, position, font_scale=0.6, color=(255, 255, 255), 
                  thickness=1, bg_color=None):
        """
        Draw text with optional background
        
        Args:
            image: Input image
            text: Text to draw
            position: (x, y) position
            font_scale: Font size
            color: Text color (BGR)
            thickness: Text thickness
            bg_color: Background color (BGR)
        """
        font = cv2.FONT_HERSHEY_SIMPLEX
        
        # Get text size for background
        text_size, baseline = cv2.getTextSize(text, font, font_scale, thickness)
        
        # Draw background if specified
        if bg_color is not None:
            x, y = position
            cv2.rectangle(image, (x - 5, y - text_size[1] - 5),
                          (x + text_size[0] + 5, y + baseline + 5), bg_color, -1)
        
        # Draw text
        cv2.putText(image, text, position, font, font_scale, color, thickness)
    
    @staticmethod
    def draw_circle(image, center, radius, color=(0, 255, 0), thickness=2):
        """
        Draw circle on image
        
        Args:
            image: Input image
            center: (x, y) center position
            radius: Circle radius
            color: BGR color
            thickness: Line thickness (-1 for filled)
        """
        cv2.circle(image, tuple(center), int(radius), color, thickness)
    
    @staticmethod
    def draw_line(image, pt1, pt2, color=(255, 255, 255), thickness=2):
        """
        Draw line on image
        
        Args:
            image: Input image
            pt1: Starting point (x, y)
            pt2: Ending point (x, y)
            color: BGR color
            thickness: Line thickness
        """
        cv2.line(image, tuple(pt1), tuple(pt2), color, thickness)
    
    @staticmethod
    def draw_centered_text(image, text, color=(255, 255, 255), font_scale=1.0):
        """
        Draw text centered on image
        
        Args:
            image: Input image
            text: Text to draw
            color: BGR color
            font_scale: Font size
        """
        font = cv2.FONT_HERSHEY_SIMPLEX
        text_size, _ = cv2.getTextSize(text, font, font_scale, 2)
        
        h, w = image.shape[:2]
        x = (w - text_size[0]) // 2
        y = (h + text_size[1]) // 2
        
        DrawingUtils.draw_text(image, text, (x, y), font_scale, color, 2)
    
    @staticmethod
    def draw_arrow(image, pt1, pt2, color=(255, 255, 255), thickness=2, arrow_size=0.3):
        """
        Draw arrow from pt1 to pt2
        
        Args:
            image: Input image
            pt1: Starting point
            pt2: Ending point
            color: BGR color
            thickness: Line thickness
            arrow_size: Arrow size factor
        """
        cv2.arrowedLine(image, tuple(pt1), tuple(pt2), color, thickness, 
                        tipLength=arrow_size)
    
    @staticmethod
    def create_bird_eye_view(image, src_points, dst_points):
        """
        Create bird's eye view using perspective transform
        
        Args:
            image: Input image
            src_points: Source points (original view)
            dst_points: Destination points (bird's eye view)
        
        Returns:
            Transformed image
        """
        src_points = np.array(src_points, dtype=np.float32)
        dst_points = np.array(dst_points, dtype=np.float32)
        
        # Get perspective transform matrix
        matrix = cv2.getPerspectiveTransform(src_points, dst_points)
        
        h, w = image.shape[:2]
        # Warp perspective
        warped = cv2.warpPerspective(image, matrix, (w, h))
        
        return warped, matrix
    
    @staticmethod
    def draw_rectangle(image, pt1, pt2, color=(0, 255, 0), thickness=2):
        """
        Draw rectangle on image
        
        Args:
            image: Input image
            pt1: Top-left corner
            pt2: Bottom-right corner
            color: BGR color
            thickness: Line thickness
        """
        cv2.rectangle(image, tuple(pt1), tuple(pt2), color, thickness)
