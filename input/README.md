# Input Videos

Place your road/dashcam videos in this directory.

## Expected Format
- **Filename**: road_video.mp4 (or configure in config.yaml)
- **Format**: MP4 video file
- **Codec**: H.264 or compatible
- **Resolution**: 640x480 or higher recommended
- **FPS**: 24, 30, or 60 FPS

## Example Videos
You can use any of these sources:
1. Dashcam recordings
2. Simulation environment videos
3. YouTube lane detection test videos
4. Your own recorded videos

## Recommended Video Properties
- Duration: 1-10 minutes for testing
- Clear lane markings
- Various lighting conditions
- Different road types (straight, curved, city, highway)

## To Get Started
1. Download a sample video from a public source or use your own
2. Place it in this directory
3. Rename to `road_video.mp4` or update config.yaml with your filename
4. Run: `python main.py`
