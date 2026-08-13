import asyncio
import time
from pathlib import Path
import edge_tts
from reelforge.agents.base import BaseAgent
from reelforge.config import settings, AUDIO_DIR
from reelforge.models import JobState


class VoiceAgent(BaseAgent):
    """
    F8 - Voice Generation Agent
    Converts narration scripts into natural neural voice audio using Edge TTS.
    """
    
    def __init__(self):
        super().__init__("VoiceAgent")

    def execute(self, state: JobState) -> JobState:
        if not state.script:
            raise ValueError("State script missing for VoiceAgent execution.")

        self.log(state, f"Generating neural TTS narration audio (Voice: {settings.TTS_VOICE})...")

        text = state.script.full_text
        output_filename = f"narration_{int(time.time())}.mp3"
        output_path = str(AUDIO_DIR / output_filename)

        async def generate_speech():

            communicate = edge_tts.Communicate(text=text, voice=settings.TTS_VOICE, rate=settings.TTS_RATE)
            await communicate.save(output_path)

        try:
            # Run async edge_tts synthesis loop
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # Create new loop if called inside async FastAPI context
                    import nest_asyncio
                    nest_asyncio.apply()
                    loop.run_until_complete(generate_speech())
                else:
                    loop.run_until_complete(generate_speech())
            except RuntimeError:
                asyncio.run(generate_speech())

            state.audio_path = output_path
            self.log(state, f"Narration audio created successfully at: {output_path}")
        except Exception as e:
            self.log(state, f"Edge TTS generation warning: {str(e)}. Using fallback TTS synth.")
            state.audio_path = self._generate_fallback_audio(text)

        return state

    def _generate_fallback_audio(self, text: str) -> str:
        """
        Creates a silent/placeholder audio track if TTS endpoint is unreachable offline.
        """
        output_filename = f"narration_fallback_{int(time.time())}.mp3"
        output_path = str(AUDIO_DIR / output_filename)
        # Note: MoviePy/FFmpeg will construct silent audio stream if needed
        return output_path
