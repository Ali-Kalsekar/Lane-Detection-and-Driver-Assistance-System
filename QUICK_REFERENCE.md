# Lane Detection System - Quick Reference Guide

## 🚀 Start Here

### 1-Minute Setup
```bash
# Install packages
pip install -r requirements.txt

# Run system
python main.py
```

### Controls
- **`q`** = Quit
- **`p`** = Pause/Play

---

## 📋 Common Tasks

### Connect Your Video
Edit `config/config.yaml`:
```yaml
video_source: input/road_video.mp4
```

### Change Parameters
Edit `config/config.yaml`:
```yaml
# Detect lanes better
canny_low_threshold: 40           # Lower = more sensitive
hough_threshold: 25               # Lower = more lines detected
history_buffer_size: 3            # Lower = faster response

# Reduce false positives
canny_low_threshold: 80           # Higher = less sensitive  
hough_threshold: 50               # Higher = fewer lines
```

### Use Different Video Source
```bash
# Webcam (index 0)
# Edit config.yaml:
video_source: 0

# Or use absolute path:
video_source: C:\Users\YourName\Videos\dashcam.mp4
```

### Find Output Files
- **Video**: `output/processed_video.mp4`
- **Logs**: `output/lane_detection_[timestamp].log`

---

## 🎚️ Important Parameters

| Parameter | Range | Default | Effect |
|-----------|-------|---------|--------|
| `canny_low_threshold` | 0-100 | 50 | Edge detection sensitivity (LOW) |
| `canny_high_threshold` | 50-255 | 150 | Edge detection sensitivity (HIGH) |
| `hough_threshold` | 10-100 | 30 | Line detection threshold |
| `history_buffer_size` | 1-20 | 5 | Lane smoothing amount |
| `departure_threshold` | 0.1-1.0 | 0.3 | Warning sensitivity |
| `roi_top_percent` | 0-1 | 0.4 | Detection area start |

---

## 🔍 Detect Lanes Better

**Problem**: Lane not detected

**Solution 1**: Adjust edge detection
```yaml
canny_low_threshold: 30   # More sensitive
canny_high_threshold: 120
```

**Solution 2**: Adjust Hough detection
```yaml
hough_threshold: 15       # More lenient
hough_min_line_length: 30
```

**Solution 3**: Enable color detection
```yaml
use_adaptive_threshold: true
```

---

## 🎨 Reduce False Detections

**Problem**: Detecting road markings that aren't lanes

**Solution 1**: Stricter thresholds
```yaml
canny_low_threshold: 80   # Less sensitive
canny_high_threshold: 180
hough_threshold: 50       # More strict
```

**Solution 2**: Adjust region of interest
```yaml
roi_top_percent: 0.5      # Focus lower
roi_bottom_percent: 1.0
```

**Solution 3**: Increase smoothing
```yaml
history_buffer_size: 8    # More filtering
```

---

## ⚡ Speed Up Processing

**Problem**: Processing is slow (low FPS)

**Solution 1**: Reduce resolution
- Edit video file: downscale before input

**Solution 2**: Disable features
```yaml
use_adaptive_threshold: false
use_perspective_transform: false
display_bird_eye_view: false
```

**Solution 3**: Faster processing
```yaml
history_buffer_size: 2    # Less smoothing
hough_threshold: 50       # Less detection work
```

---

## 🌙 Night Driving Mode

Enable for low-light videos:
```yaml
enable_night_mode: true
night_gamma_correction: 1.8

# Also adjust thresholds
canny_low_threshold: 80
canny_high_threshold: 200
```

---

## 🚨 Customize Warnings

Change warning sensitivity:
```yaml
departure_threshold: 0.2   # Very sensitive (warns often)
departure_threshold: 0.5   # Less sensitive (warns rarely)
```

Change warning color:
```yaml
warning_color: [0, 0, 255]     # Red (BGR format)
warning_color: [0, 255, 255]   # Yellow
warning_color: [255, 0, 0]     # Blue
```

---

## 📊 Display Options

Show/hide elements:
```yaml
display_fps: true              # Show FPS counter
display_offset: true           # Show lateral offset
display_curvature: true        # Show road curvature
display_warning: true          # Show warnings
display_bird_eye_view: false   # Show bird's eye view
```

---

## 🐛 Troubleshooting

| Issue | Fix |
|-------|-----|
| "Video not found" | Check video path in config.yaml |
| "ModuleNotFoundError" | `pip install -r requirements.txt` |
| Lanes not detected | Increase `history_buffer_size`, adjust thresholds |
| Too many false positives | Decrease `hough_threshold`, increase `roi_top_percent` |
| Slow FPS | Disable features, enable night_mode=false |
| Crashes | Increase `history_buffer_size`, restart |

---

## 📁 File Locations

```
Project Root:           lane_detection_system/
Your Video:             input/road_video.mp4
Processed Video:        output/processed_video.mp4
Logs:                   output/lane_detection_*.log
Config:                 config/config.yaml
Source Code:            [module_name]/
```

---

## 🎯 Preset Configurations

### Highway Driving
```yaml
canny_low_threshold: 40
canny_high_threshold: 120
hough_threshold: 25
history_buffer_size: 7
departure_threshold: 0.2
roi_top_percent: 0.3
```

### City Driving
```yaml
canny_low_threshold: 60
canny_high_threshold: 180
hough_threshold: 40
history_buffer_size: 3
departure_threshold: 0.5
roi_top_percent: 0.5
```

### Night Driving
```yaml
enable_night_mode: true
night_gamma_correction: 1.8
canny_low_threshold: 80
canny_high_threshold: 200
use_adaptive_threshold: true
hough_threshold: 35
```

### Performance Mode
```yaml
canny_low_threshold: 60
hough_threshold: 40
history_buffer_size: 2
use_perspective_transform: false
use_adaptive_threshold: false
```

### Accuracy Mode
```yaml
canny_low_threshold: 40
canny_high_threshold: 100
hough_threshold: 20
history_buffer_size: 10
use_adaptive_threshold: true
use_perspective_transform: true
```

---

## 💡 Tips & Tricks

### Tip 1: Test Different Thresholds
Copy config.yaml to config_backup.yaml, then experiment with values.

### Tip 2: Check Logs for Errors
```bash
# View recent log
tail -f output/lane_detection_*.log
```

### Tip 3: Record Your Own Video
Use any dashcam, phone, or simulation to create test videos.

### Tip 4: Use ROI Masking
Adjust `roi_top_percent` to focus on the road area:
```yaml
roi_top_percent: 0.4   # Detect from 40% down
```

### Tip 5: Enable Debug Logging
```yaml
log_level: DEBUG
```

---

## 🔧 Advanced Configuration

### Custom Region of Interest
Edit `preprocessing/image_preprocessor.py`:
```python
# Modify trapezoid vertices for custom ROI shape
vertices = np.array([
    [0, bottom_y],
    [int(w * 0.2), top_y],         # Adjust percentages here
    [int(w * 0.8), top_y],
    [w, bottom_y]
], dtype=np.int32)
```

### Custom Color Detection
Edit `preprocessing/image_preprocessor.py`:
```python
# Modify HSV color ranges for different lane colors
lower_white = np.array([0, 0, 200])
upper_white = np.array([180, 30, 255])
```

### Custom Warning Timing
Edit `config/config.yaml`:
```python
# Add to LaneWarning.__init__ in warning_system/lane_warning.py
self.warning_cooldown = 30  # Frames between warnings
```

---

## 📚 Documentation Map

| Document | Purpose | Read When |
|----------|---------|-----------|
| README.md | Full documentation | Learning system |
| SETUP.md | Installation guide | First time setup |
| PROJECT_SUMMARY.md | Complete overview | Understanding architecture |
| config/config.yaml | Configuration | Customizing system |
| output/README.md | Output files | Understanding results |

---

## 🎓 Learning Path

1. **Start**: Run `python main.py` with default config
2. **Understand**: Read README.md and PROJECT_SUMMARY.md
3. **Customize**: Edit config.yaml for your video
4. **Optimize**: Adjust parameters based on results
5. **Integrate**: Use modules in your own code
6. **Deploy**: Prepare for production use

---

## 📞 Quick Help

### Check Installation
```python
import cv2, numpy, scipy, yaml
print("All installed!")
```

### Test Video Loading
```bash
python
>>> from video_loader.video_reader import VideoReader
>>> reader = VideoReader('input/road_video.mp4')
>>> ret, frame = reader.read_frame()
>>> print(f"Loaded: {frame.shape}")
```

### View Recent Logs
```bash
# Latest log file
ls -t output/lane_detection_*.log | head -1
```

---

## 🎨 Output Legend

### Visual Elements on Screen
```
Green Lines      = Detected lanes
Yellow Line      = Lane center
Green Dot        = Vehicle position
Red Border       = Warning alert
Green Rectangle  = Lane fill area
```

### Text Displays
```
FPS: XX.X        = Processing speed
Frame: N/M       = Current/total frame
Offset: ±X.XXm   = Distance from center
Position: CENTER = Position in lane
Curvature: XXXXpx = Road curvature radius
Road: STRAIGHT   = Road type
```

---

## 🚀 One-Command Solutions

### Process video with custom config
1. Edit `config/config.yaml`
2. Run: `python main.py`

### Use webcam instead
Edit config.yaml: `video_source: 0`

### Process faster
Set: `history_buffer_size: 2`

### Process with more accuracy
Set: `history_buffer_size: 10`

---

**Last Updated**: 2024
**Language**: Python 3.8+
**Dependencies**: OpenCV, NumPy, SciPy, PyYAML

For detailed information, refer to README.md and SETUP.md
