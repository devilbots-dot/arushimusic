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
            try:
                title = result["title"]
                title = re.sub("\W+", " ", title)
                title = short_title(title)
            except:
                title = "Unsupported Title"

            try:
                duration = result["duration"]
            except:
                duration = "Unknown"

            thumbnail = result["thumbnails"][0]["url"].split("?")[0]

            try:
                views = result["viewCount"]["short"]
            except:
                views = "Unknown"

            try:
                channel = result["channel"]["name"]
            except:
                channel = "Unknown Channel"

        # -------- DOWNLOAD YT THUMB --------
        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    async with aiofiles.open(f"cache/thumb{videoid}.png", "wb") as f:
                        await f.write(await resp.read())

        youtube = Image.open(f"cache/thumb{videoid}.png").convert("RGBA")

        # ============ BACKGROUND ============
        background = youtube.resize((1280, 720)).filter(ImageFilter.GaussianBlur(radius=18))
        background = ImageEnhance.Brightness(background).enhance(0.45)
        draw = ImageDraw.Draw(background)

        # SPRINKLES
        for _ in range(240):
            x = random.randint(0, 1280)
            y = random.randint(0, 720)
            r = random.randint(1, 3)
            draw.ellipse((x, y, x+r, y+r), fill="white")

        # MUSIC NOTES BG
        music_font = ImageFont.truetype("SONALI/assets/font.ttf", 26)
        for _ in range(15):
            draw.text(
                (random.randint(100, 1180), random.randint(40, 520)),
                "♪",
                fill="white",
                font=music_font,
            )

        # ============ DIAMONDS ============
        diamond = Image.new("RGBA", (260, 260), (255,255,255,0))
        ddraw = ImageDraw.Draw(diamond)
        ddraw.polygon(
            [(130,0),(260,130),(130,260),(0,130)],
            outline="white",
            width=6
        )

        try:
            note_img = Image.open("SONALI/assets/diamond_note.png").convert("RGBA")
            note_img = note_img.resize((110, 110))
            diamond.paste(note_img, (75, 75), note_img)
        except Exception as e:
            print("diamond_note.png load error:", e)

        background.paste(diamond, (40, 90), diamond)
        background.paste(diamond, (980, 90), diamond)

        # ============ CENTER CIRCLE ============
        CIRCLE_SIZE = 360
        yt_thumb = youtube.resize((CIRCLE_SIZE, CIRCLE_SIZE))

        mask = Image.new("L", (CIRCLE_SIZE, CIRCLE_SIZE), 0)
        ImageDraw.Draw(mask).ellipse((0,0,CIRCLE_SIZE,CIRCLE_SIZE), fill=255)

        circ = Image.new("RGBA", (CIRCLE_SIZE, CIRCLE_SIZE))
        circ.paste(yt_thumb, (0,0), mask)

        # ============ SPIKES BASE LAYERS ============
        RING_PADDING = 70
        ring_size = CIRCLE_SIZE + (RING_PADDING * 2)

        ring = Image.new("RGBA", (ring_size, ring_size), (0,0,0,0))
        rdraw = ImageDraw.Draw(ring)

        # 3 layer circles
        rdraw.ellipse((15,15,ring_size-15,ring_size-15), outline="white", width=5)
        rdraw.ellipse((40,40,ring_size-40,ring_size-40), outline="white", width=3)
        rdraw.ellipse((65,65,ring_size-65,ring_size-65), outline="white", width=2)

        center = ring_size // 2
        radius = (ring_size // 2) - 25

        # static spikes for PNG
        for angle in range(0, 360, 6):
            rad = math.radians(angle)
            x1 = center + int(radius * math.cos(rad))
            y1 = center + int(radius * math.sin(rad))
            spike_length = random.randint(20, 60)
            x2 = center + int((radius + spike_length) * math.cos(rad))
            y2 = center + int((radius + spike_length) * math.sin(rad))
            rdraw.line([(x1, y1), (x2, y2)], fill="white", width=5)

        ring_x = 330
        ring_y = 40
        circle_x = ring_x + RING_PADDING
        circle_y = ring_y + RING_PADDING

        background.paste(ring, (ring_x, ring_y), ring)
        background.paste(circ, (circle_x, circle_y), circ)

        # ============ FONTS ============
        arial = ImageFont.truetype("SONALI/assets/font2.ttf", 28)
        font = ImageFont.truetype("SONALI/assets/font.ttf", 28)
        bold_font = ImageFont.truetype("SONALI/assets/font.ttf", 30)
        icon_font = ImageFont.truetype("SONALI/assets/DejaVuSans.ttf", 42)

        # WATERMARK
        tw,_ = draw.textsize("@Starmusic by devil", font=font)
        draw.text((1280-tw-10, 10), "@Starmusic by devil", fill="yellow", font=font)

        # CHANNEL LEFT
        draw.text((60, 360), channel, fill="white", font=arial)

        # VIEWS RIGHT
        draw.text((1000, 360), views, fill="white", font=arial)

        # TITLE CENTER
        tt_w,_ = draw.textsize(title, font=font)
        draw.text(((1280-tt_w)//2, 520), title, fill="cyan", font=font)

        # TIMELINE
        timeline = "❍━━━ლ━━━❍"
        tl_w,_ = draw.textsize(timeline, font=bold_font)
        draw.text(((1280-tl_w)//2, 560), timeline, fill="white", font=bold_font)

        # PLAYER BUTTONS
        controls = "🔀   ⏮   ▶️   ⏭   🔁"
        cw,_ = draw.textsize(controls, font=icon_font)
        draw.text(((1280-cw)//2, 610), controls, fill="white", font=icon_font)

        # ============ HYBRID GIF (STATIC CENTER + ANIMATED SPIKES) ============
        frames = []

        for i in range(5):
            temp = background.copy()
            tdraw = ImageDraw.Draw(temp)

            for angle in range(0, 360, 7):
                rad = math.radians(angle)

                x1 = center + int(radius * math.cos(rad))
                y1 = center + int(radius * math.sin(rad))

                spike_length = random.randint(15 + i*8, 45 + i*10)

                x2 = center + int((radius + spike_length) * math.cos(rad))
                y2 = center + int((radius + spike_length) * math.sin(rad))

                tdraw.line(
                    [(x1, y1), (x2, y2)],
                    fill=(255, 255, 255, 180),
                    width=4
                )

            frames.append(temp)

        # save animated gif
        frames[0].save(
            f"cache/{videoid}.gif",
            save_all=True,
            append_images=frames[1:],
            duration=180,
            loop=0
        )

        # save static png for telegram
        background.save(f"cache/{videoid}.png")

        try:
            os.remove(f"cache/thumb{videoid}.png")
        except:
            pass

        return f"cache/{videoid}.png"

    except Exception as e:
        print(e)
        return YOUTUBE_IMG_URL
