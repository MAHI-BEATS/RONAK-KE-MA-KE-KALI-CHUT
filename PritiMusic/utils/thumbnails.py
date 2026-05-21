import os
import re
import random
import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from unidecode import unidecode
from py_yt import VideosSearch

from PritiMusic import app
from config import YOUTUBE_IMG_URL

def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    newImage = image.resize((newWidth, newHeight))
    return newImage

def clear(text):
    list_words = text.split(" ")
    title = ""
    for i in list_words:
        if len(title) + len(i) < 60:
            title += " " + i
    return title.strip()

# ✅ Helper for Random Fallback
def get_random_fallback_img():
    if YOUTUBE_IMG_URL:
        if isinstance(YOUTUBE_IMG_URL, list):
            return random.choice(YOUTUBE_IMG_URL)
        return YOUTUBE_IMG_URL
    return "https://telegra.ph/file/2e3d368e77c449c287430.jpg" # Fallback

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
                title = title.title()
            except:
                title = "Unsupported Title"
            try:
                duration = result["duration"]
            except:
                duration = "Unknown Mins"
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            try:
                views = result["viewCount"]["short"]
            except:
                views = "Unknown Views"
            try:
                channel = result["channel"]["name"]
            except:
                channel = "Unknown Channel"

        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    async with aiofiles.open(f"cache/thumb{videoid}.png", mode="wb") as f:
                        await f.write(await resp.read())

        youtube = Image.open(f"cache/thumb{videoid}.png")
        image1 = changeImageSize(1280, 720, youtube)
        
        # Convert to RGBA for transparency support
        background = image1.convert("RGBA")
        
        # 1. Background Blur
        background = background.filter(filter=ImageFilter.BoxBlur(10))
        enhancer = ImageEnhance.Brightness(background)
        background = enhancer.enhance(0.5)
        
        # 2. Add Black Attractive Card Overlay
        overlay = Image.new("RGBA", background.size, (0, 0, 0, 0))
        draw_overlay = ImageDraw.Draw(overlay)
        
        # Card Box Coordinates (Left, Top, Right, Bottom)
        card_box = [60, 400, 1220, 650]
        
        try:
            # Rounded rectangle for modern look (Pillow 8.2.0+)
            draw_overlay.rounded_rectangle(
                card_box, 
                radius=25, 
                fill=(10, 10, 10, 210),   # Semi-transparent black
                outline=(255, 255, 255, 80), # Subtle white border
                width=3
            )
        except AttributeError:
            # Fallback for older PIL versions
            draw_overlay.rectangle(card_box, fill=(10, 10, 10, 210), outline=(255, 255, 255, 80), width=3)
            
        background = Image.alpha_composite(background, overlay)
        draw = ImageDraw.Draw(background)
        
        # 3. Fonts Loading
        try:
            arial = ImageFont.truetype("PritiMusic/assets/font2.ttf", 30)
            font = ImageFont.truetype("PritiMusic/assets/font.ttf", 35) 
            stylish_font = ImageFont.truetype("PritiMusic/assets/font.ttf", 40)
        except:
            arial = ImageFont.load_default()
            font = ImageFont.load_default()
            stylish_font = ImageFont.load_default()
            
        # 4. Elements INSIDE the Card
        # Channel & Views
        draw.text((90, 430), f"{channel} | {views[:23]}", (200, 200, 200), font=arial)
        
        # Title
        draw.text((90, 480), clear(title), (255, 255, 255), font=font)
        
        # Progress Bar (Background Line - Inactive)
        draw.line([(90, 570), (1190, 570)], fill=(255, 255, 255, 90), width=6, joint="curve")
        
        # Progress Bar (Active Line)
        draw.line([(90, 570), (380, 570)], fill="white", width=6, joint="curve")
        
        # Progress Dot
        draw.ellipse([(370, 558), (394, 582)], outline="white", fill="white", width=4)
        
        # Duration & Timer
        draw.text((90, 595), "00:00", (255, 255, 255), font=arial)
        draw.text((1080, 595), f"{duration[:23]}", (255, 255, 255), font=arial)
        
        # 5. Elements OUTSIDE (Bottom Left & Right)
        # Left Bottom Text
        draw.text((60, 670), "BETA BOT HUB", (255, 215, 0), font=stylish_font) # Gold/Yellow color
        
        # Right Bottom Text (Bot Name)
        bot_name = "PritiMusic"
        if hasattr(app, "name") and app.name:
            bot_name = app.name
        
        # Calculate width to align right (approximate approach for PIL without getbbox)
        # Assuming ~20 pixels per character for size 40 font
        right_x = 1220 - (len(bot_name) * 20) 
        draw.text((right_x, 670), bot_name, (255, 215, 0), font=stylish_font)

        try:
            os.remove(f"cache/thumb{videoid}.png")
        except:
            pass
            
        background.save(f"cache/{videoid}.png")
        return f"cache/{videoid}.png"
        
    except Exception as e:
        print(e)
        return get_random_fallback_img()
