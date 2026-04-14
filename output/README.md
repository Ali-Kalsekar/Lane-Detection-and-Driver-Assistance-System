# Output Files

This directory contains processed results from the lane detection system.

## Contents

### processed_video.mp4
The main output video file containing:
- Detected lane lines (green)
- Lane area fill (semi-transparent)
- Vehicle position marker
- Lane center reference line
- Real-time FPS counter
- Curvature information
- Vehicle offset from lane center
- Lane departure warnings (when active)
- Road type classification

### lane_detection_[timestamp].log
Detailed system log file containing:
- Initialization messages
- Frame-by-frame processing status
- Performance metrics
- Error messages and warnings
- Detection statistics
- Warning events
- System cleanup information

## Log File Analysis

### Example Log Entries
```
2024-01-15 10:30:05 - LaneDetectionSystem - INFO - Configuration loaded: config/config.yaml
2024-01-15 10:30:05 - LaneDetectionSystem - INFO - Video loaded: input/road_video.mp4
2024-01-15 10:30:05 - LaneDetectionSystem - INFO - Video properties: 640x480 @ 30 FPS
2024-01-15 10:30:06 - LaneDetectionSystem - INFO - Total frames processed: 1500
2024-01-15 10:30:06 - LaneDetectionSystem - INFO - Average FPS: 28.5
```

## Performance Metrics

After processing completion, the log will show:
- Total frames processed
- Average FPS achieved
- Total elapsed time
- Lane detector statistics
- Warning system statistics

## Video Output Details

### Visual Elements
1. **Green Lane Lines** - Detected left and right lanes
2. **Line Thickness** - Configurable (default: 3 pixels)
3. **Semi-transparent Fill** - Lane area highlighted
4. **Yellow Center Line** - Lane center reference
5. **Green Dot** - Vehicle position (image center)
6. **Red Border** - Lane departure warning alert

### Text Overlays (top-left)
- FPS: X.X (frames per second)
- Frame: N/TOTAL (current/total frame count)
- Offset: ±X.XXm (lateral offset in meters)
- Position: CENTER/LEFT/RIGHT
- Curvature: XXXX px (radius in pixels)
- Road: STRAIGHT/GENTLE_CURVE/MODERATE_CURVE/TIGHT_CURVE

### Warnings
- **Lane Departure**: Red border + warning text
- **Tight Curves**: Yellow warning in upper-left
- **Detection Failed**: Lane tracking lost notification

## Usage

1. Run `python main.py` to generate processed_video.mp4
2. Check the console and log file for statistics
3. Review video output for visual validation
4. Analyze log file for debugging if needed

## File Management

To keep outputs organized:
- Rename output files with date/time timestamps
- Archive logs for long-term analysis
- Keep multiple processed videos for comparison
- Use log analysis tools for pattern detection

## Troubleshooting

If output files are missing or corrupted:
1. Check file permissions in the output directory
2. Verify disk space availability
3. Review error messages in the log file
4. Ensure video_writer initialized successfully

## Integration with Other Tools

The processed video can be used with:
- Video analysis tools
- Incident review systems
- Fleet management platforms
- Insurance claim documentation
- Training and testing datasets
