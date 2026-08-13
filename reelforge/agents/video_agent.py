import time
import os
import subprocess
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
import imageio_ffmpeg
from reelforge.agents.base import BaseAgent
from reelforge.config import settings, VIDEOS_DIR
from reelforge.models import JobState

class VideoAgent(BaseAgent):
    """
    F10 & F11 - Video Composition & Audio Sync Agent
    High-performance 9:16 vertical MP4 video renderer (1080x1920, 30fps) using OpenCV & FFmpeg.
    """
    
    def __init__(self):
        super().__init__("VideoAgent")

    def execute(self, state: JobState) -> JobState:
        if not state.script or not state.visual_paths:
            raise ValueError("Script and visual paths are required for VideoAgent rendering.")

        self.log(state, f"Composing 9:16 vertical video Reel (1080x1920 @ {settings.VIDEO_FPS}fps)...")

        visuals = state.visual_paths
        segments = state.script.segments
        w, h = settings.VIDEO_WIDTH, settings.VIDEO_HEIGHT
        fps = settings.VIDEO_FPS

        temp_video_filename = f"temp_silent_{int(time.time())}.mp4"
        temp_video_path = str(VIDEOS_DIR / temp_video_filename)
        output_filename = f"reel_{int(time.time())}.mp4"
        final_video_path = str(VIDEOS_DIR / output_filename)

        # 1. Render Video Frames using OpenCV VideoWriter
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(temp_video_path, fourcc, fps, (w, h))

        for idx, segment in enumerate(segments):
            dur = segment.duration_seconds
            num_frames = int(dur * fps)
            img_path = visuals[idx % len(visuals)]

            if os.path.exists(img_path):
                img = Image.open(img_path).convert("RGB")
                img = img.resize((w, h))
                frame_bgr = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

                for _ in range(num_frames):
                    writer.write(frame_bgr)

        writer.release()
        self.log(state, "Visual frame sequence rendered successfully.")

        # 2. Merge Narration Audio using imageio_ffmpeg / FFmpeg
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

        if state.audio_path and os.path.exists(state.audio_path) and os.path.getsize(state.audio_path) > 0:
            cmd = [
                ffmpeg_exe, "-y",
                "-i", temp_video_path,
                "-i", state.audio_path,
                "-c:v", "libx264",
                "-preset", "ultrafast",
                "-c:a", "aac",
                "-shortest",
                final_video_path
            ]
        else:
            cmd = [
                ffmpeg_exe, "-y",
                "-i", temp_video_path,
                "-c:v", "libx264",
                "-preset", "ultrafast",
                final_video_path
            ]

        try:
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            state.video_path = final_video_path
            self.log(state, f"Video composition & H.264 encoding completed successfully! Final MP4: {final_video_path}")
        except Exception as e:
            self.log(state, f"FFmpeg sync fallback: {str(e)}. Using silent video stream.")
            state.video_path = temp_video_path
        finally:
            if os.path.exists(temp_video_path) and state.video_path != temp_video_path:
                try:
                    os.remove(temp_video_path)
                except Exception:
                    pass

        return state
