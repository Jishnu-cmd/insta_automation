import time
from PIL import Image, ImageDraw, ImageFont
from reelforge.agents.base import BaseAgent
from reelforge.config import settings, COVERS_DIR
from reelforge.models import JobState


class CoverAgent(BaseAgent):
    """
    F12 - Cover Generation Agent
    Generates striking 9:16 Reel cover/thumbnail image (1080x1920) optimized for Instagram feed grid.
    """
    
    def __init__(self):
        super().__init__("CoverAgent")

    def execute(self, state: JobState) -> JobState:
        if not state.topic:
            raise ValueError("Topic state required for CoverAgent.")

        self.log(state, "Generating 1080x1920 Reel cover thumbnail image...")

        w, h = settings.VIDEO_WIDTH, settings.VIDEO_HEIGHT
        img = Image.new("RGBA", (w, h), (14, 18, 28, 255))
        draw = ImageDraw.Draw(img)

        # Gradient background
        for y in range(h):
            r = int(14 + (y / h) * 15)
            g = int(18 + (y / h) * 20)
            b = int(28 + (y / h) * 35)
            draw.line([(0, y), (w, y)], fill=(r, g, b, 255))

        # Glowing accent border & backdrop
        draw.rounded_rectangle([50, 400, w - 50, 1500], radius=30, fill=(24, 30, 46, 240), outline=(0, 230, 150, 255), width=4)

        try:
            font_category = ImageFont.truetype("arialbd.ttf", 32)
            font_title = ImageFont.truetype("arialbd.ttf", 64)
            font_badge = ImageFont.truetype("arialbd.ttf", 36)
            font_handle = ImageFont.truetype("arial.ttf", 28)
        except Exception:
            font_category = ImageFont.load_default()
            font_title = ImageFont.load_default()
            font_badge = ImageFont.load_default()
            font_handle = ImageFont.load_default()

        # Category Tag
        draw.rounded_rectangle([100, 460, 450, 520], radius=15, fill=(0, 230, 150, 40), outline=(0, 230, 150, 255), width=2)
        draw.text((120, 473), f" 🔥 {state.topic.category.upper()} ", fill=(0, 240, 160, 255), font=font_category)

        # Main Title Wrapped
        title = state.topic.title
        words = title.split()
        lines = []
        curr = []
        for word in words:
            curr.append(word)
            if len(" ".join(curr)) > 16:
                curr.pop()
                lines.append(" ".join(curr))
                curr = [word]
        if curr:
            lines.append(" ".join(curr))

        y_pos = 580
        for line in lines[:5]:
            draw.text((100, y_pos), line, fill=(255, 255, 255, 255), font=font_title)
            y_pos += 85

        # Format Badge
        y_pos += 40
        draw.rounded_rectangle([100, y_pos, 460, y_pos + 70], radius=20, fill=(0, 150, 255, 255))
        draw.text((130, y_pos + 15), f" [ {state.topic.format.value} ] ", fill=(255, 255, 255, 255), font=font_badge)

        # Account branding
        draw.text((w // 2 - 160, h - 140), f"{settings.BRAND_NAME} | {settings.INSTAGRAM_HANDLE}", fill=(140, 160, 190, 220), font=font_handle)

        output_filename = f"cover_{int(time.time())}.png"
        output_path = str(COVERS_DIR / output_filename)
        img.save(output_path, "PNG")


        state.cover_path = output_path
        self.log(state, f"Reel cover generated successfully at: {output_path}")
        return state
