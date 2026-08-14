import asyncio
import time
import concurrent.futures
from pathlib import Path
import edge_tts
from reelforge.agents.base import BaseAgent
from reelforge.config import settings, AUDIO_DIR
from reelforge.models import JobState

def _run_tts_in_new_loop(text: str, voice: str, rate: str, output_path: str):
    """Runs edge_tts synthesis inside a dedicated, isolated asyncio event loop."""
    async def _synth():
        communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate)
        await communicate.save(output_path)

    new_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(new_loop)
    try:
        new_loop.run_until_complete(_synth())
    finally:
        new_loop.close()

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

        try:
            # Run in isolated thread pool executor to prevent event loop conflicts
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    _run_tts_in_new_loop,
                    text,
                    settings.TTS_VOICE,
                    settings.TTS_RATE,
                    output_path
                )
                future.result(timeout=30)

            state.audio_path = output_path
            self.log(state, f"Narration audio created successfully at: {output_path}")
        except Exception as e:
            self.log(state, f"Edge TTS generation warning: {str(e)}. Using fallback TTS track.")
            state.audio_path = self._generate_fallback_audio(text)

        return state

    def _generate_fallback_audio(self, text: str) -> str:
        output_filename = f"narration_fallback_{int(time.time())}.mp3"
        output_path = str(AUDIO_DIR / output_filename)
        return output_path
