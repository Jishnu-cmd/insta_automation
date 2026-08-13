import sys
import os
import time
import tempfile
import subprocess
from pathlib import Path
from typing import Optional
from PIL import Image, ImageDraw, ImageFont
from reelforge.config import settings, IMAGES_DIR, TEMP_DIR
from reelforge.models import CodeExecutionResult

class SandboxRunner:
    """
    Executes Python code snippets in an isolated, timed subprocess.
    Captures stdout/stderr and renders visual code/terminal card assets.
    """
    
    def __init__(self, timeout_seconds: float = 5.0):
        self.timeout_seconds = timeout_seconds

    def execute_python_code(self, code_snippet: str) -> CodeExecutionResult:
        start_time = time.time()
        
        # Create a temporary file inside isolated temp directory
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", dir=TEMP_DIR, delete=False, encoding="utf-8") as temp_file:
            temp_file.write(code_snippet)
            temp_file_path = temp_file.name

        try:
            process = subprocess.Popen(
                [sys.executable, temp_file_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                env={**os.environ, "PYTHONUNBUFFERED": "1", "PYTHONIOENCODING": "utf-8"}
            )

            
            try:
                stdout, stderr = process.communicate(timeout=self.timeout_seconds)
                exit_code = process.returncode
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
                exit_code = -1
                stderr += f"\n[Execution Timed Out after {self.timeout_seconds}s]"
        except Exception as e:
            stdout, stderr = "", f"[Execution Error: {str(e)}]"
            exit_code = 1
        finally:
            if os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                except Exception:
                    pass

        execution_time = round((time.time() - start_time) * 1000, 2)
        
        # Render code + terminal output image card
        card_image_path = self.render_terminal_card(code_snippet, stdout, stderr, exit_code)
        
        return CodeExecutionResult(
            code=code_snippet,
            language="python",
            executed=(exit_code == 0),
            stdout=stdout.strip(),
            stderr=stderr.strip(),
            exit_code=exit_code,
            execution_time_ms=execution_time,
            output_image_path=card_image_path
        )

    def render_terminal_card(self, code: str, stdout: str, stderr: str, exit_code: int) -> str:
        """
        Renders a sleek dark-mode IDE/Terminal window PNG (1080x1920 9:16 format).
        """
        width, height = settings.VIDEO_WIDTH, settings.VIDEO_HEIGHT
        img = Image.new("RGBA", (width, height), (15, 18, 25, 255))
        draw = ImageDraw.Draw(img)

        # Background gradient / decorative glow
        for y in range(height):
            r = int(15 + (y / height) * 10)
            g = int(18 + (y / height) * 12)
            b = int(25 + (y / height) * 20)
            draw.line([(0, y), (width, y)], fill=(r, g, b, 255))

        # Terminal Container (1000x1400 centered)
        margin_x = 40
        margin_y = 200
        box_width = width - (margin_x * 2)
        box_height = 1400

        # Glassmorphism container background
        draw.rounded_rectangle(
            [margin_x, margin_y, margin_x + box_width, margin_y + box_height],
            radius=20,
            fill=(24, 28, 38, 240),
            outline=(45, 55, 75, 255),
            width=2
        )

        # Terminal Header Bar
        header_height = 60
        draw.rounded_rectangle(
            [margin_x, margin_y, margin_x + box_width, margin_y + header_height],
            radius=20,
            fill=(32, 38, 52, 255)
        )

        # Window Action Buttons (Red, Yellow, Green dots)
        draw.ellipse([margin_x + 20, margin_y + 20, margin_x + 36, margin_y + 36], fill=(255, 95, 87, 255))
        draw.ellipse([margin_x + 45, margin_y + 20, margin_x + 61, margin_y + 36], fill=(254, 188, 46, 255))
        draw.ellipse([margin_x + 70, margin_y + 20, margin_x + 86, margin_y + 36], fill=(40, 201, 64, 255))

        # Title in Header
        try:
            font_title = ImageFont.truetype("arial.ttf", 22)
            font_code = ImageFont.truetype("consola.ttf", 26)
            font_output = ImageFont.truetype("consola.ttf", 24)
        except Exception:
            font_title = ImageFont.load_default()
            font_code = ImageFont.load_default()
            font_output = ImageFont.load_default()

        draw.text((margin_x + box_width // 2 - 80, margin_y + 16), "main.py - Flow Tech Sandbox", fill=(160, 175, 200, 255), font=font_title)

        # Draw Code Content
        code_y = margin_y + header_height + 40
        draw.text((margin_x + 30, code_y), "# Flow Tech AI Sandbox Output", fill=(100, 130, 170, 255), font=font_code)
        code_y += 45

        lines = code.split("\n")[:18]  # Limit lines for canvas fit
        for idx, line in enumerate(lines):
            draw.text((margin_x + 30, code_y), f"{idx+1:2d} | {line}", fill=(220, 230, 245, 255), font=font_code)
            code_y += 36

        # Output Section Divider
        code_y += 30
        draw.line([(margin_x + 20, code_y), (margin_x + box_width - 20, code_y)], fill=(50, 65, 90, 255), width=2)
        code_y += 20

        draw.text((margin_x + 30, code_y), "TERMINAL OUTPUT:", fill=(0, 230, 150, 255), font=font_title)
        code_y += 40

        output_text = stdout if stdout else (stderr if stderr else "[Process completed with no output]")
        output_lines = output_text.split("\n")[:8]
        output_color = (0, 255, 170, 255) if exit_code == 0 else (255, 100, 100, 255)

        for line in output_lines:
            draw.text((margin_x + 30, code_y), f"> {line}", fill=output_color, font=font_output)
            code_y += 36

        # Branding Footer
        draw.text((width // 2 - 120, height - 120), f"{settings.BRAND_NAME} | {settings.INSTAGRAM_HANDLE}", fill=(120, 140, 170, 200), font=font_title)

        output_filename = f"terminal_card_{int(time.time())}.png"
        output_path = str(IMAGES_DIR / output_filename)
        img.save(output_path, "PNG")
        return output_path

