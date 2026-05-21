import os
import re
import random
import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from unidecode import unidecode
from py_yt import VideosSearch

from PritiMusic import app
import config

def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    return image.resize((newWidth, newHeight))

def clear(text):
    # Emojis aur weird characters ko clean karne ke liye unidecode use kiya
    try:
        text = unidecode(text)
    except Exception:
        pass
    list_words = text.split(" ")
    title = ""
    for i in list_words:
        if len(title) + len(i) < 60:
            title += " " + i
    return title.strip()

# ✅ Safe Random Fallback Image Link String return karega
def get_random_fallback_img():
    if hasattr(config, "YOUTUBE_IMG_URL") and config.YOUTUBE_IMG_URL:
        if isinstance(config.YOUTUBE_IMG_URL, list):
            return random.choice(config.YOUTUBE_IMG_URL)
        return config.YOUTUBE_IMG_URL
    return "https://files.catbox.moe/n22tbs.jpg"

async def get_thumb(videoid):
    if os.path.isfile(f"cache/{videoid}.png"):
        return f"cache/{videoid}.png"

    url = f"https://www.youtube.com/watch?v={videoid}"
    try:
        results = VideosSearch(url, limit=1)
        next_result = await results.next()
        if not next_result or "result" not in next_result or not next_result["result"]:
            return get_random_fallback_img()

        for result in next_result["result"]:
            try:
                title = result["title"]
                title = re.sub(r"\W+", " ", title)
                title = title.title()
            except Exception:
                title = "Unsupported Title"
            try:
                duration = result["duration"]
            except Exception:
                duration = "Unknown Mins"
            
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            
            try:
                views = result["viewCount"]["short"]
            except Exception:
                views = "Unknown Views"
            try:
                channel = result["channel"]["name"]
            except Exception:
                channel = "Unknown Channel"

        # Create cache folder if it doesn't exist
        if not os.path.exists("cache"):
            os.makedirs("cache")

        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    async with aiofiles.open(f"cache/thumb{videoid}.png", mode="wb") as f:
                        await f.write(await resp.read())
                else:
                    return get_random_fallback_img()

        youtube = Image.open(f"cache/thumb{videoid}.png")
        image1 = changeImageSize(1280, 720, youtube)
        
        # Convert to RGBA for blending layers
        background = image1.convert("RGBA")
        background = background.filter(filter=ImageFilter.BoxBlur(10))
        enhancer = ImageEnhance.Brightness(background)
        background = enhancer.enhance(0.5)
        
        overlay = Image.new("RGBA", background.size, (0, 0, 0, 0))
        draw_overlay = ImageDraw.Draw(overlay)
        
        card_box = [60, 400, 1220, 650]
        
        try:
            draw_overlay.rounded_rectangle(
                card_box, 
                radius=25, 
                fill=(10, 10, 10, 210),   
                outline=(255, 255, 255, 80), 
                width=3
            )
        except AttributeError:
            draw_overlay.rectangle(card_box, fill=(10, 10, 10, 210), outline=(255, 255, 255, 80), width=3)
            
        background = Image.alpha_composite(background, overlay)
        draw = ImageDraw.Draw(background)
        
        # Safe font loader paths
        font_paths = ["PritiMusic/assets/font2.ttf", "PritiMusic/assets/font.ttf"]
        try:
            arial = ImageFont.truetype(font_paths[0], 30)
            font = ImageFont.truetype(font_paths[1], 35) 
            stylish_font = ImageFont.truetype(font_paths[1], 40)
        except Exception:
            arial = ImageFont.load_default()
            font = ImageFont.load_default()
            stylish_font = ImageFont.load_default()
            
        # Draw text insides
        draw.text((90, 430), f"{channel} | {views}", (200, 200, 200), font=arial)
        draw.text((90, 480), clear(title), (255, 255, 255), font=font)
        
        # Progress bars
        draw.line([(90, 570), (1190, 570)], fill=(255, 255, 255, 90), width=6)
        draw.line([(90, 570), (380, 570)], fill="white", width=6)
        draw.ellipse([(370, 558), (394, 582)], outline="white", fill="white", width=4)
        
        draw.text((90, 595), "00:00", (255, 255, 255), font=arial)
        draw.text((1080, 595), f"{duration}", (255, 255, 255), font=arial)
        
        # Footer Branding
        draw.text((60, 670), "BETA BOT HUB", (255, 215, 0), font=stylish_font)
        
        bot_name = "PRITI MUSIC"
        if hasattr(app, "name") and app.name:
            bot_name = str(app.name).upper()
        
        # Dynamic Text Alignment for Bot Name to avoid layout overlapping
        try:
            if hasattr(stylish_font, "getbbox"):
                text_w = stylish_font.getbbox(bot_name)[2]
            else:
                text_w = draw.textsize(bot_name, font=stylish_font)[0]
            right_x = 1220 - text_w
        except Exception:
            right_x = 1220 - (len(bot_name) * 20)

        draw.text((right_x, 670), bot_name, (255, 215, 0), font=stylish_font)

        try:
            os.remove(f"cache/thumb{videoid}.png")
        except Exception:
            pass
            
        background.save(f"cache/{videoid}.png")
        return f"cache/{videoid}.png"
        
    except Exception as e:
        print(f"Thumbnail Error: {e}")
        return get_random_fallback_img()
