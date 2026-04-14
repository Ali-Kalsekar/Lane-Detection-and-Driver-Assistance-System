# Lane Detection System - Setup & Installation Guide

## Quick Start (5 minutes)

### 1. Install Dependencies
```bash
cd lane_detection_system
pip install -r requirements.txt
```

### 2. Add Video File
- Place your video file in `input/` folder
- Optional: Rename to `road_video.mp4` or update `config/config.yaml`

### 3. Run the System
```bash
python main.py
```

### 4. View Results
- Watch real-time processing in the window
- Output video saved to `output/processed_video.mp4`
- Logs saved to `output/lane_detection_[timestamp].log`

---

## Detailed Installation

### System Requirements

#### Operating System
- Windows 7+
- macOS 10.12+
- Linux (Ubuntu 18.04+)

#### Python Environment
- Python 3.8 or higher
- pip package manager
- Virtual environment recommended

#### Hardware
**Minimum:**
- 4GB RAM
- Dual-core CPU
- 1GB free disk space

**Recommended:**
- 8GB+ RAM
- Quad-core CPU
- GPU support (CUDA for NVIDIA)
- SSD storage

#### Internet Connection
- Required for pip package installation

### Step 1: Setup Python Environment

#### Option A: Using Virtual Environment (Recommended)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

#### Option B: Using Conda

```bash
conda create -n lane_detection python=3.10
conda activate lane_detection
```

### Step 2: Install Required Packages

```bash
pip install -r requirements.txt
```

**Packages Installed:**
- `opencv-python` (4.8.1.78) - Computer vision library
- `numpy` (1.24.3) - Numerical computing
- `matplotlib` (3.7.2) - Plotting library
- `scipy` (1.11.2) - Scientific computing
- `PyYAML` (6.0.1) - Configuration file parsing

**Installation Time:** 5-10 minutes depending on internet speed

### Step 3: Verify Installation

Test that all packages are installed correctly:

```bash
python -c "import cv2, numpy, scipy, yaml; print('All packages installed successfully!')"
```

Expected output:
```
All packages installed successfully!
```

### Step 4: Prepare Input Video

#### Get a Sample Video

Option 1: **Use a dashcam video**
- Found on YouTube (search "dashcam highway footage")
- Personal dashcam recordings

Option 2: **Use simulation videos**
- CARLA simulator output
- Apollo autonomous driving dataset
- Udacity self-driving car dataset

Option 3: **Download from datasets**
- BDD100K (Berkeley)
- KITTI dataset
- Comma2k19

#### Recommended Video Properties
```
Format:     MP4 (H.264 codec)
Resolution: 640x480 to 1280x720
FPS:        24, 30, or 60
Duration:   1-10 minutes
Quality:    Clear lane markings visible
```

#### File Placement
```
Place video at:
    lane_detection_system/input/road_video.mp4

Alternative:
    Place video anywhere and update config/config.yaml:
    video_source: path/to/your/video.mp4
```

### Step 5: Verify Setup

Create a simple test script to verify everything works:

```python
# test_setup.py
import cv2
import numpy as np
from preprocessing.image_preprocessor import ImagePreprocessor
from lane_detection.lane_detector import LaneDetector

print("✓ OpenCV version:", cv2.__version__)
print("✓ NumPy version:", np.__version__)

# Test preprocessing
pre = ImagePreprocessor()
print("✓ Preprocessor initialized")

# Test lane detector
detector = LaneDetector()
print("✓ Lane detector initialized")

print("\n✓ All systems ready!")
```

Run test:
```bash
python test_setup.py
```

---

## Configuration Setup

### Basic Configuration

The system uses `config/config.yaml` for all parameters. No coding required!

#### 1. Video Input/Output

```yaml
# Your video source
video_source: input/road_video.mp4
video_source: 0                    # Alternative: use webcam (index 0)

# Processed output
output_video: output/processed_video.mp4
```

#### 2. Edge Detection Parameters

```yaml
# Canny Edge Detection
canny_low_threshold: 50            # Lower threshold (50-100 typical)
canny_high_threshold: 150          # Upper threshold (150-200 typical)

# Gaussian Blur
gaussian_blur_kernel: [5, 5]       # Kernel size (odd numbers: 3, 5, 7, 9)
```

#### 3. Lane Detection Parameters

```yaml
# Hough Transform settings
hough_rho: 2                       # Distance resolution (1-5 typical)
hough_theta: 1                     # Angle resolution in degrees
hough_threshold: 30                # Accumulator threshold (20-50 typical)
hough_min_line_length: 50          # Minimum line length in pixels
hough_max_line_gap: 20             # Maximum gap between line segments

# Lane tracking
history_buffer_size: 5             # Frames for smoothing (3-10 typical)
```

#### 4. Warning System

```yaml
# Lane departure threshold (0 to 1)
departure_threshold: 0.3           # 0.2 = very sensitive, 0.5 = lenient

# Warning colors (BGR format)
warning_color: [0, 0, 255]         # Red in BGR
lane_color: [0, 255, 0]            # Green in BGR
```

#### 5. Display Options

```yaml
display_fps: true                  # Show frames per second
display_offset: true               # Show lateral offset
display_curvature: true            # Show road curvature
display_warning: true              # Show warnings
display_bird_eye_view: false       # Show bird's eye view
```

### Advanced Configuration

#### Video Processing

```yaml
fps_target: 30                     # Target processing speed

# Region of Interest (ROI)
roi_top_percent: 0.4               # Start detection from 40% down
roi_bottom_percent: 1.0            # Process to bottom of frame
```

#### Night Driving Support

```yaml
enable_night_mode: false           # Enable/disable
night_gamma_correction: 1.5        # Gamma value (1.2-2.0 typical)
```

#### Adaptive Processing

```yaml
use_adaptive_threshold: false      # Adaptive thresholding
use_perspective_transform: true    # Bird's eye view
adaptive_block_size: 11            # Block size (odd numbers)
```

#### Logging

```yaml
log_level: INFO                    # DEBUG, INFO, WARNING, ERROR
log_file: output/lane_detection.log
```

### Configuration Profiles

#### Quick Configuration Change

**Copy-Paste Sections:**

**High-Quality (Good light, clear lanes):**
```yaml
canny_low_threshold: 40
canny_high_threshold: 120
hough_threshold: 25
history_buffer_size: 7
```

**Robust Mode (Variable conditions):**
```yaml
canny_low_threshold: 50
canny_high_threshold: 150
hough_threshold: 30
history_buffer_size: 5
```

**Performance Mode (Fastest):**
```yaml
canny_low_threshold: 60
canny_high_threshold: 180
hough_threshold: 40
history_buffer_size: 2
use_adaptive_threshold: false
display_bird_eye_view: false
```

---

## Running the System

### Command Line Usage

```bash
# Basic execution
python main.py

# With custom config (if using different config files)
# Edit main.py line: system = LaneDetectionSystem(config_path='config/config.yaml')
python main.py
```

### During Execution

**Keyboard Controls:**
- **`q`** - Quit and exit
- **`p`** - Pause/Resume video
- **`Esc`** - Emergency exit

**What You'll See:**
1. Processing window with real-time video
2. Green lane lines on detected lanes
3. Yellow center line reference
4. FPS counter and statistics
5. Warning alerts when appropriate

### Expected Output

**Console Output:**
```
================================================
Lane Detection and Driver Assistance System Initialized
================================================
Configuration loaded: config/config.yaml
Video loaded: input/road_video.mp4
Video properties: 640x480 @ 30 FPS
All components initialized successfully
Starting video processing...
```

**Processing Window:**
- Real-time video with overlays
- FPS counter (top-left)
- Lane information display
- Warning messages (if triggered)

**Log File:**
- Created in `output/` directory
- Timestamped filename
- Detailed processing information
- Performance metrics

---

## Troubleshooting Installation

### Issue: ModuleNotFoundError for OpenCV

**Cause:** OpenCV not installed
**Solution:**
```bash
pip install --upgrade opencv-python
```

### Issue: Python version error

**Cause:** Python < 3.8
**Solution:**
```bash
python --version
# Install Python 3.10+ from python.org
```

### Issue: Video file not found

**Cause:** Incorrect path or missing video
**Solution:**
1. Verify file exists in `input/` folder
2. Check filename in config.yaml matches
3. Use absolute path if needed

### Issue: Permission denied errors

**Cause:** Insufficient file permissions
**Solution:**
```bash
# Linux/macOS
chmod 755 lane_detection_system/output

# Windows (run as Administrator)
python main.py
```

### Issue: Low FPS or slow processing

**Cause:** High resolution or slow CPU
**Solution:**
1. Reduce video resolution
2. Increase `history_buffer_size` for smoothing
3. Disable visualization
4. Use GPU acceleration (if available)

---

## Performance Tuning

### Optimize for Speed

1. Lower resolution:
   - Resize in video preprocessing
   - Edit `ImagePreprocessor` to downscale

2. Reduce detection frequency:
   - Process every Nth frame
   - Increase `history_buffer_size`

3. Simplify visualization:
   - Set `display_bird_eye_view: false`
   - Reduce `history_buffer_size: 2`

### Optimize for Accuracy

1. Enable all features:
   - `use_adaptive_threshold: true`
   - `use_perspective_transform: true`
   - `display_bird_eye_view: true`

2. Increase buffer:
   - `history_buffer_size: 10`

3. Stricter thresholds:
   - `canny_low_threshold: 30`
   - `canny_high_threshold: 200`

---

## Next Steps After Setup

1. **Process Your Video:** Run `python main.py`
2. **Review Output:** Check `output/processed_video.mp4`
3. **Analyze Logs:** Review `output/lane_detection_*.log`
4. **Tune Configuration:** Adjust `config/config.yaml` for your video
5. **Integrate Code:** Use modules in your own projects
6. **Deploy:** Prepare for real-world deployment

---

## Getting Help

### Debugging Steps

1. **Enable Debug Logging:**
   ```yaml
   log_level: DEBUG
   ```

2. **Check Log File:**
   ```bash
   cat output/lane_detection_*.log
   ```

3. **Test Individual Modules:**
   ```python
   # Test preprocessor
   from preprocessing.image_preprocessor import ImagePreprocessor
   import cv2
   
   img = cv2.imread('input/frame.jpg')
   pre = ImagePreprocessor()
   result = pre.preprocess(img)
   cv2.imshow('Preprocessed', result)
   cv2.waitKey(0)
   ```

4. **Test Video Loading:**
   ```python
   from video_loader.video_reader import VideoReader
   
   reader = VideoReader('input/road_video.mp4')
   ret, frame = reader.read_frame()
   print(f"Frame loaded: {ret}, Shape: {frame.shape}")
   ```

### Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| Lanes not detected | Poor video quality | Adjust canny thresholds |
| False positives | Shadows/markings | Increase `hough_threshold` |
| Slow processing | High resolution | Downscale video |
| Crashes | Memory error | Reduce `history_buffer_size` |
| Color distortion | GPU memory | Disable GPU, use CPU |

---

## System Health Check

After setup, run this verification:

```python
# verify_system.py
import os
import yaml
import cv2
from video_loader.video_reader import VideoReader

# Check directory structure
dirs = [
    'config', 'video_loader', 'preprocessing', 'lane_detection',
    'curvature_estimation', 'vehicle_position', 'warning_system',
    'utils', 'input', 'output'
]

print("Checking directory structure...")
for d in dirs:
    if os.path.exists(d):
        print(f"  ✓ {d}/")
    else:
        print(f"  ✗ {d}/ MISSING")

# Check config file
print("\nChecking configuration...")
if os.path.exists('config/config.yaml'):
    with open('config/config.yaml') as f:
        config = yaml.safe_load(f)
    print(f"  ✓ {len(config)} config parameters loaded")
else:
    print("  ✗ config.yaml not found")

# Check video source
print("\nChecking video source...")
video_source = config.get('video_source', 'input/road_video.mp4')
if os.path.exists(video_source):
    reader = VideoReader(video_source)
    w, h = reader.get_resolution()
    fps = reader.get_frame_rate()
    print(f"  ✓ Video loaded: {w}x{h} @ {fps} FPS")
    reader.release()
else:
    print(f"  ✗ Video not found: {video_source}")

print("\n✓ System ready to run!")
```

Run verification:
```bash
python verify_system.py
```

---

## Next Level: Integration & Deployment

### Integrate into Your Project

```python
from lane_detection_system.main import LaneDetectionSystem

# Create system instance
system = LaneDetectionSystem('config/config.yaml')
system.initialize_components()

# Process video (or single frame)
system.run()
```

### Deployment Checklist

- [ ] Test with production video
- [ ] Validate output accuracy
- [ ] Measure performance metrics
- [ ] Configure for target platform
- [ ] Set up error handling
- [ ] Implement logging/monitoring
- [ ] Prepare for scaling
- [ ] Document integration points

---

**Setup Complete! You're ready to run the Lane Detection System.**
