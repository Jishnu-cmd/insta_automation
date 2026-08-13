import json
import time
from pathlib import Path
from reelforge.agents.base import BaseAgent
from reelforge.config import settings, TEMP_DIR
from reelforge.models import JobState


class SubtitleAgent(BaseAgent):
    """
    F9 - Subtitle Agent
    Generates word-level/phrase-level synchronized subtitle subtitle metadata & SRT files.
    """
    
    def __init__(self):
        super().__init__("SubtitleAgent")

    def execute(self, state: JobState) -> JobState:
        if not state.script:
            raise ValueError("Script state required for SubtitleAgent.")

        self.log(state, "Generating synchronized word/phrase kinetic subtitles...")

        srt_lines = []
        current_time = 0.0
        subtitle_index = 1

        for segment in state.script.segments:
            duration = segment.duration_seconds
            words = segment.narration.split()
            if not words:
                continue

            # Break into 3-word chunks for punchy 9:16 vertical subtitle display
            chunk_size = 3
            chunks = [words[i:i+chunk_size] for i in range(0, len(words), chunk_size)]
            time_per_chunk = duration / len(chunks)

            for chunk in chunks:
                start_t = current_time
                end_t = current_time + time_per_chunk
                phrase = " ".join(chunk).upper()

                start_srt = self._format_timestamp(start_t)
                end_srt = self._format_timestamp(end_t)

                srt_lines.append(f"{subtitle_index}")
                srt_lines.append(f"{start_srt} --> {end_srt}")
                srt_lines.append(phrase)
                srt_lines.append("")

                subtitle_index += 1
                current_time = end_t

        srt_content = "\n".join(srt_lines)
        output_filename = f"subtitles_{int(time.time())}.srt"
        output_path = str(TEMP_DIR / output_filename)

        with open(output_path, "w", encoding="utf-8") as f:

            f.write(srt_content)

        state.subtitle_path = output_path
        self.log(state, f"Subtitles generated successfully at: {output_path}")
        return state

    def _format_timestamp(self, seconds: float) -> str:
        millis = int((seconds - int(seconds)) * 1000)
        secs = int(seconds) % 60
        mins = (int(seconds) // 60) % 60
        hours = int(seconds) // 3600
        return f"{hours:02d}:{mins:02d}:{secs:02d},{millis:03d}"
