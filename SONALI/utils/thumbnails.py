import os
import re
import random
import math
import aiohttp
import aiofiles
from SONALI import app
from config import YOUTUBE_IMG_URL
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from py_yt import VideosSearch


def short_title(title):
    words = title.split()
    return " ".join(words[:5]) + ("..." if len(words) > 5 else "")


async def get_thumb(videoid):

    if os.path.isfile(f"cache/{videoid}.png"):
        return f"cache/{videoid}.png"

    url = f"https://www.youtube.com/watch?v={videoid}"

    try:
        results = VideosSearch(url, limit=1)
        for result in (await results.next())["result"]:
            title = short_title(result.get("title", "Music Track"))
            duration = result.get("duration", "00:00")
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            views = result.get("viewCount", {}).get("short", "Unknown")
            channel = result.get("channel", {}).get("name", "Unknown Channel")

        # -------- DOWNLOAD YT THUMB --------
        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                data = await resp.read()

        temp_path = f"cache/temp_{videoid}.png"
        with open(temp_path, "wb") as f:
            f.write(data)

        youtube = Image.open(temp_path).convert("RGBA")

        # ============ BACKGROUND ============
        background = youtube.resize((1280, 720)).filter(
            ImageFilter.GaussianBlur(radius=18)
        )
        background = ImageEnhance.Brightness(background).enhance(0.45)
        draw = ImageDraw.Draw(background)

        # -------- SPARKLES --------
        for _ in range(180):
            x = random.randint(0, 1280)
            y = random.randint(0, 720)
            r = random.randint(1, 3)
            draw.ellipse((x, y, x + r, y + r), fill="white")

        # ============ CENTER CIRCLE (THODA CHOTA + UP) ============
        CIRCLE = 320
        yt_thumb = youtube.resize((CIRCLE, CIRCLE))

        mask = Image.new("L", (CIRCLE, CIRCLE), 0)
        mdraw = ImageDraw.Draw(mask)
        mdraw.ellipse((0, 0, CIRCLE, CIRCLE), fill=255)

        circ = Image.new("RGBA", (CIRCLE, CIRCLE))
        circ.paste(yt_thumb, (0, 0), mask)

        # light border
        border = Image.new("RGBA", (CIRCLE + 12, CIRCLE + 12), (255, 255, 255, 0))
        bdraw = ImageDraw.Draw(border)
        bdraw.ellipse((2, 2, CIRCLE + 10, CIRCLE + 10), outline="white", width=4)

        cx = (1280 - (CIRCLE + 12)) // 2
        cy = 70

        background.paste(border, (cx, cy), border)
        background.paste(circ, (cx + 6, cy + 6), circ)

        # ============ TITLE (CENTER, CYAN, BOLD) ============
        font_title = ImageFont.truetype("SONALI/assets/font.ttf", 36)

        title_w, title_h = draw.textsize(title, font=font_title)
        draw.text(
            ((1280 - title_w) // 2, 430),
            title,
            fill="cyan",
            font=font_title,
        )

        # ============ CHANNEL + VIEWS (WHITE, RIGHT DIAMOND KE NICHE) ============
        font_small = ImageFont.truetype("SONALI/assets/font2.ttf", 24)

        draw.text(
            (900, 380),
            f"{channel} | {views}",
            fill="white",
            font=font_small,
        )

        # ============ MEDIUM TIMELINE (CENTER, WHITE) ============
        start_x = 380
        end_x = 900
        line_y = 480

        draw.text((340, 470), "00:00", fill="white", font=font_small)
        draw.line([(start_x, line_y), (end_x, line_y)], fill="white", width=5)
        draw.text((920, 470), duration, fill="white", font=font_small)

        # ============ PLAYER BUTTONS (CODE-DRAWN) ============
        # PREVIOUS
        draw.polygon(
            [(520, 520), (560, 540), (520, 560)],
            fill="white",
        )

        # PLAY (CIRCLE)
        draw.ellipse((610, 515, 690, 585), outline="white", width=3)
        draw.polygon(
            [(635, 535), (665, 550), (635, 565)],
            fill="white",
        )

        # NEXT
        draw.polygon(
            [(740, 520), (700, 540), (740, 560)],
            fill="white",
        )

        # SHUFFLE ICON (two arrows)
        draw.line([(780, 535), (830, 535)], fill="white", width=2)
        draw.line([(830, 535), (820, 525)], fill="white", width=2)
        draw.line([(820, 545), (830, 535)], fill="white", width=2)

        # ============ WATERMARK ============
        font_wm = ImageFont.truetype("SONALI/assets/font.ttf", 26)
        draw.text(
            (1280 - 260, 10),
            "@Starmusic by devil",
            fill="yellow",
            font=font_wm,
        )

        # cleanup temp
        try:
            os.remove(temp_path)
        except:
            pass

        final_path = f"cache/{videoid}.png"
        background.save(final_path)
        return final_path

    except Exception as e:
        print("Thumbnail error:", e)
        return YOUTUBE_IMG_URL
