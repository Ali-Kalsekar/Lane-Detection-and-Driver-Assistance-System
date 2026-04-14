"""Logger utility module for the Lane Detection System"""

import logging
import os
from datetime import datetime


class SystemLogger:
    """Centralized logging system for the lane detection application"""
    
    _instance = None
    _logger = None
    
    def __new__(cls):
        """Implement singleton pattern"""
        if cls._instance is None:
            cls._instance = super(SystemLogger, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize logger if not already done"""
        if self._initialized:
            return
        
        self._initialized = True
        self._setup_logger()
    
    def _setup_logger(self):
        """Setup logger configuration"""
        log_dir = "output"
        os.makedirs(log_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"lane_detection_{timestamp}.log")
        
        # Create logger
        self._logger = logging.getLogger("LaneDetectionSystem")
        self._logger.setLevel(logging.DEBUG)
        
        # Clear existing handlers
        self._logger.handlers.clear()
        
        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        self._logger.addHandler(file_handler)
        self._logger.addHandler(console_handler)
    
    def get_logger(self):
        """Get logger instance"""
        return self._logger
    
    @staticmethod
    def debug(msg):
        """Log debug message"""
        SystemLogger()._logger.debug(msg)
    
    @staticmethod
    def info(msg):
        """Log info message"""
        SystemLogger()._logger.info(msg)
    
    @staticmethod
    def warning(msg):
        """Log warning message"""
        SystemLogger()._logger.warning(msg)
    
    @staticmethod
    def error(msg):
        """Log error message"""
        SystemLogger()._logger.error(msg)
    
    @staticmethod
    def critical(msg):
        """Log critical message"""
        SystemLogger()._logger.critical(msg)


# Create singleton instance
logger = SystemLogger().get_logger()
