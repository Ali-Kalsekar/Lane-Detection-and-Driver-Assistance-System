"""Curvature estimation module for lane analysis"""

import numpy as np
from scipy.optimize import curve_fit
from utils.logger import SystemLogger


class CurvatureCalculator:
    """Calculates road curvature from detected lanes"""
    
    def __init__(self, poly_degree=2, pixels_per_meter_x=3.7/700, 
                 pixels_per_meter_y=30/720):
        """
        Initialize curvature calculator
        
        Args:
            poly_degree: Degree of polynomial for fitting (usually 2 for parabola)
            pixels_per_meter_x: X-axis pixel to meter conversion
            pixels_per_meter_y: Y-axis pixel to meter conversion
        """
        self.logger = SystemLogger().get_logger()
        self.poly_degree = poly_degree
        self.pixels_per_meter_x = pixels_per_meter_x
        self.pixels_per_meter_y = pixels_per_meter_y
        
        # Store fitted polynomials
        self.left_poly = None
        self.right_poly = None
        self.center_poly = None
    
    def calculate_curvature(self, left_lane, right_lane):
        """
        Calculate road curvature from left and right lanes
        
        Args:
            left_lane: Left lane points [(x, y), ...]
            right_lane: Right lane points [(x, y), ...]
            
        Returns:
            dict: Curvature information
        """
        result = {
            'left_curvature': None,
            'right_curvature': None,
            'center_curvature': None,
            'average_curvature': None,
            'is_curved': False
        }
        
        # Calculate left lane curvature
        if left_lane and len(left_lane) > 3:
            left_curv = self._fit_and_calculate_curvature(left_lane)
            result['left_curvature'] = left_curv
        
        # Calculate right lane curvature
        if right_lane and len(right_lane) > 3:
            right_curv = self._fit_and_calculate_curvature(right_lane)
            result['right_curvature'] = right_curv
        
        # Calculate center lane curvature
        if left_lane and right_lane:
            center_lane = self._get_center_lane(left_lane, right_lane)
            if center_lane and len(center_lane) > 3:
                center_curv = self._fit_and_calculate_curvature(center_lane)
                result['center_curvature'] = center_curv
        
        # Calculate average
        curvatures = [c for c in [result['left_curvature'], 
                                  result['right_curvature'],
                                  result['center_curvature']] if c is not None]
        
        if curvatures:
            result['average_curvature'] = np.mean(curvatures)
            result['is_curved'] = result['average_curvature'] < 1000  # Threshold for curved road
        
        return result
    
    def _fit_and_calculate_curvature(self, lane_points):
        """
        Fit polynomial to lane and calculate curvature
        
        Args:
            lane_points: List of (x, y) points
            
        Returns:
            float: Radius of curvature in pixels
        """
        if not lane_points or len(lane_points) < 3:
            return None
        
        try:
            points = np.array(lane_points, dtype=np.float32)
            
            # Sort by y coordinate (from top to bottom)
            points = points[np.argsort(points[:, 1])]
            
            x = points[:, 0]
            y = points[:, 1]
            
            # Fit polynomial
            coeffs = np.polyfit(y, x, self.poly_degree)
            poly = np.poly1d(coeffs)
            
            # Calculate derivatives for curvature formula
            # For curve x = f(y): curvature = |d²x/dy²| / (1 + (dx/dy)²)^(3/2)
            
            # First derivative (dx/dy)
            dpoly = np.polyder(poly)
            
            # Second derivative (d²x/dy²)
            d2poly = np.polyder(dpoly)
            
            # Evaluate at middle point for stable calculation
            y_eval = y[len(y)//2]
            
            first_deriv = dpoly(y_eval)
            second_deriv = d2poly(y_eval)
            
            # Calculate radius of curvature
            if second_deriv == 0:
                return float('inf')
            
            curvature_radius = (1 + first_deriv**2)**(3/2) / abs(second_deriv)
            
            return curvature_radius
        
        except Exception as e:
            self.logger.warning(f"Error calculating curvature: {str(e)}")
            return None
    
    def _get_center_lane(self, left_lane, right_lane):
        """
        Calculate center lane from left and right lanes
        
        Args:
            left_lane: Left lane points
            right_lane: Right lane points
            
        Returns:
            Center lane points
        """
        center_lane = []
        
        # Get common y range
        left_y = set([p[1] for p in left_lane])
        right_y = set([p[1] for p in right_lane])
        common_y = sorted(left_y.intersection(right_y))
        
        for y in common_y:
            # Find x values for this y
            left_x = None
            right_x = None
            
            for x, py in left_lane:
                if abs(py - y) < 2:
                    left_x = x
                    break
            
            for x, py in right_lane:
                if abs(py - y) < 2:
                    right_x = x
                    break
            
            if left_x is not None and right_x is not None:
                center_x = (left_x + right_x) / 2
                center_lane.append((center_x, y))
        
        return center_lane if center_lane else None
    
    def get_polynomial_fit(self, lane_points):
        """
        Get polynomial fit for a lane
        
        Args:
            lane_points: Lane points
            
        Returns:
            numpy poly1d object
        """
        if not lane_points or len(lane_points) < 3:
            return None
        
        points = np.array(lane_points, dtype=np.float32)
        points = points[np.argsort(points[:, 1])]
        
        x = points[:, 0]
        y = points[:, 1]
        
        coeffs = np.polyfit(y, x, self.poly_degree)
        return np.poly1d(coeffs)
    
    def evaluate_lane_at_y(self, lane_points, y_value):
        """
        Evaluate lane x position at specific y coordinate
        
        Args:
            lane_points: Lane points
            y_value: Y coordinate
            
        Returns:
            X coordinate at given y
        """
        poly = self.get_polynomial_fit(lane_points)
        
        if poly is None:
            return None
        
        return int(poly(y_value))
    
    def classify_road_type(self, curvature):
        """
        Classify road type based on curvature
        
        Args:
            curvature: Radius of curvature value
            
        Returns:
            str: Road type classification
        """
        if curvature is None or curvature == float('inf'):
            return "STRAIGHT"
        
        if curvature < 300:
            return "TIGHT_CURVE"
        elif curvature < 800:
            return "MODERATE_CURVE"
        elif curvature < 2000:
            return "GENTLE_CURVE"
        else:
            return "STRAIGHT"
    
    def reset(self):
        """Reset calculator"""
        self.left_poly = None
        self.right_poly = None
        self.center_poly = None
