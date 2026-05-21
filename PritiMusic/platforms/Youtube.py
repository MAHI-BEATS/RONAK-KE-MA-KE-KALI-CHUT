import asyncio
import glob
import json
import os
import random
import re
from concurrent.futures import ThreadPoolExecutor
from typing import Union
import string
import requests
import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from ytSearch import VideosSearch, Playlist
from PritiMusic import LOGGER
from PritiMusic.utils.database import is_on_off
from PritiMusic.utils.formatters import time_to_seconds
from config import YT_API_KEY, YTPROXY_URL as YTPROXY

logger = LOGGER(__name__)

def cookie_txt_file():
    try:
        folder_path = f"{os.getcwd()}/cookies"
        filename = f"{os.getcwd()}/cookies/logs.csv"
        txt_files = glob.glob(os.path.join(folder_path, '*.txt'))
        if not txt_files:
            raise FileNotFoundError("No .txt files found in the specified folder.")
        cookie_txt_file = random.choice(txt_files)
        with open(filename, 'a') as file:
            file.write(f'Choosen File : {cookie_txt_file}\n')
        return f"""cookies/{str(cookie_txt_file).split("/")[-1]}"""
    except:
        return None


class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.status = "https://www.youtube.com/oembed?url="
        self.listbase = "https://youtube.com/playlist?list="
        self.reg = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
        self.dl_stats = {
            "total_requests": 0,
            "okflix_downloads": 0,
            "cookie_downloads": 0,
            "existing_files": 0
        }
        # Blocking synchronous HTTP requests ke liye Thread Pool Executor
        self.executor = ThreadPoolExecutor(max_workers=5)


    async def exists(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if re.search(self.regex, link):
            return True
        else:
            return False

    async def url(self, message_1: Message) -> Union[str, None]:
        messages = [message_1]
        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)
        text = ""
        offset = None
        length = None
        for message in messages:
            if offset:
                break
            if message.entities:
                for entity in message.entities:
                    if entity.type == MessageEntityType.URL:
                        text = message.text or message.caption
                        offset, length = entity.offset, entity.length
                        break
            elif message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
        if offset in (None,):
            return None
        return text[offset : offset + length]

    async def details(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        if "?si=" in link:
            link = link.split("?si=")[0]
        elif "&si=" in link:
            link = link.split("&si=")[0]

        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            title = result["title"]
            duration_min = result["duration"]
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            vidid = result["id"]
            if str(duration_min) == "None":
                duration_sec = 0
            else:
                duration_sec = int(time_to_seconds(duration_min))
        return title, duration_min, duration_sec, thumbnail, vidid

    async def title(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        if "?si=" in link:
            link = link.split("?si=")[0]
        elif "&si=" in link:
            link = link.split("&si=")[0]
            
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            title = result["title"]
        return title

    async def duration(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        if "?si=" in link:
            link = link.split("?si=")[0]
        elif "&si=" in link:
            link = link.split("&si=")[0]

        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            duration = result["duration"]
        return duration

    async def thumbnail(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        if "?si=" in link:
            link = link.split("?si=")[0]
        elif "&si=" in link:
            link = link.split("&si=")[0]

        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
        return thumbnail

    async def video(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        if "?si=" in link:
            link = link.split("?si=")[0]
        elif "&si=" in link:
            link = link.split("&si=")[0]

        proc = await asyncio.create_subprocess_exec(
            "yt-dlp",
            "-g",
            "-f",
            "best[height<=?720][width<=?1280]",
            f"{link}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if stdout:
            return 1, stdout.decode().split("\n")[0]
        else:
            return 0, stderr.decode()

    async def playlist(self, link, limit, user_id, videoid: Union[bool, str] = None):
        if videoid:
            link = self.listbase + link
        if "&" in link:
            link = link.split("&")[0]
        if "?si=" in link:
            link = link.split("?si=")[0]
        elif "&si=" in link:
            link = link.split("&si=")[0]

        playlist = await Playlist.get(link)
        if playlist:
            videos = []
            for video in playlist["videos"][:limit]:
                try:
                    duration = video.get("duration")
                    if duration:
                        duration_sec = int(time_to_seconds(duration))
                    else:
                        duration_sec = 0
                    videos.append({
                        "vidid": video["id"],
                        "title": video.get("title", "Unknown"),
                        "duration_min": duration,
                        "duration_sec": duration_sec,
                        "thumbnail": video.get("thumbnails", [{}])[0].get("url", "").split("?")[0] if video.get("thumbnails") else "",
                    })
                except:
                    continue
            return videos
        return None

    async def track(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        if "?si=" in link:
            link = link.split("?si=")[0]
        elif "&si=" in link:
            link = link.split("&si=")[0]

        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            title = result["title"]
            duration_min = result["duration"]
            vidid = result["id"]
            yturl = result["link"]
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
        track_details = {
            "title": title,
            "link": yturl,
            "vidid": vidid,
            "duration_min": duration_min,
            "thumb": thumbnail,
        }
        return track_details, vidid

    async def formats(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        if "?si=" in link:
            link = link.split("?si=")[0]
        elif "&si=" in link:
            link = link.split("&si=")[0]
        ytdl_opts = {"quiet": True}
        ydl = yt_dlp.YoutubeDL(ytdl_opts)
        with ydl:
            formats_available = []
            r = ydl.extract_info(link, download=False)
            for format in r["formats"]:
                try:
                    str(format["format"])
                except:
                    continue
                if not "dash" in str(format["format"]).lower():
                    try:
                        format["format"]
                        format["filesize"]
                        format["format_id"]
                        format["ext"]
                        format["format_note"]
                    except:
                        continue
                    formats_available.append(
                        {
                            "format": format["format"],
                            "filesize": format["filesize"],
                            "format_id": format["format_id"],
                            "ext": format["ext"],
                            "format_note": format["format_note"],
                            "yturl": link,
                        }
                    )
        return formats_available, link

    async def slider(self, link: str, query_type: int, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        if "?si=" in link:
            link = link.split("?si=")[0]
        elif "&si=" in link:
            link = link.split("&si=")[0]

        try:
            results = []
            search = VideosSearch(link, limit=10)
            search_results = (await search.next()).get("result", [])

            # Filter videos longer than 1 hour
            for result in search_results:
                duration_str = result.get("duration", "0:00")
                try:
                    parts = duration_str.split(":")
                    duration_secs = 0
                    if len(parts) == 3:
                        duration_secs = int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
                    elif len(parts) == 2:
                        duration_secs = int(parts[0]) * 60 + int(parts[1])

                    if duration_secs <= 3600:
                        results.append(result)
                except (ValueError, IndexError):
                    continue

            if not results or query_type >= len(results):
                raise ValueError("No suitable videos found within duration limit")

            selected = results[query_type]
            return (
                selected["title"],
                selected["duration"],
                selected["thumbnails"][0]["url"].split("?")[0],
                selected["id"]
            )

        except Exception as e:
            logger.error(f"Error in slider: {str(e)}")
            raise ValueError("Failed to fetch video details")

    async def download(
        self,
        link: str,
        mystic,
        video: Union[bool, str] = None,
        videoid: Union[bool, str] = None,
        songaudio: Union[bool, str] = None,
        songvideo: Union[bool, str] = None,
        format_id: Union[bool, str] = None,
        title: Union[bool, str] = None,
    ) -> str:
        
        # UnboundLocalError fix karne ke liye link extraction block
        if videoid:
            vid_id = link
            link = self.base + link
        else:
            # Agar direct full link pass ho rahi ho to ID nikalna zaroori hai backend proxy hit karne ke liye
            if "youtu.be/" in link:
                vid_id = link.split("youtu.be/")[-1].split(/[?#]/)[0]
            elif "v=" in link:
                vid_id = link.split("v=")[1].split("&")[0]
            else:
                vid_id = link

        loop = asyncio.get_running_loop()

        def create_session():
            session = requests.Session()
            retries = Retry(total=3, backoff_factor=0.1)
            session.mount('http://', HTTPAdapter(max_retries=retries))
            session.mount('https://', HTTPAdapter(max_retries=retries))
            return session

        # Network requests ko dynamic dynamic executor ke sath async bnaya taaki main thread block na ho
        def sync_download(url, filepath, headers):
            try:
                session = create_session()
                response = session.get(url, headers=headers, stream=True, timeout=60, allow_redirects=True)
                response.raise_for_status()
                
                chunk_size = 1024 * 1024  
                with open(filepath, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        if chunk:
                            file.write(chunk)
                return filepath
            except Exception as e:
                logger.error(f"Requests download failed: {str(e)}")
                if os.path.exists(filepath):
                    os.remove(filepath)
                return None

        def sync_fetch_info(url, headers):
            try:
                session = create_session()
                res = session.get(url, headers=headers, timeout=60)
                return res.json()
            except Exception as e:
                logger.error(f"Info fetch failed: {str(e)}")
                return None

        async def download_with_requests(url, filepath, headers=None):
            return await loop.run_in_executor(self.executor, sync_download, url, filepath, headers)

        async def audio_dl(vid_id):
            try:
                if not YT_API_KEY or not YTPROXY:
                    logger.error("API KEY or Endpoint not set in config!")
                    return None
                
                headers = {
                    "x-api-key": f"{YT_API_KEY}",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                }
                filepath = os.path.join("downloads", f"{vid_id}.mp3")
                if os.path.exists(filepath):
                    return filepath
                
                songData = await loop.run_in_executor(self.executor, sync_fetch_info, f"{YTPROXY}/info/{vid_id}", headers)
                if not songData: return None

                status = songData.get('status')
                if status == 'success':
                    audio_url = songData['audio_url']                    
                    return await download_with_requests(audio_url, filepath, headers)
                elif status == 'error':
                    logger.error(f"API Error: {songData.get('message', 'Unknown error')}")
                return None
            except Exception as e:
                logger.error(f"Error in audio download: {str(e)}")
                return None
        
        async def video_dl(vid_id):
            try:
                if not YT_API_KEY or not YTPROXY:
                    logger.error("API KEY or Endpoint not set in config!")
                    return None
                
                headers = {
                    "x-api-key": f"{YT_API_KEY}",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                }
                filepath = os.path.join("downloads", f"{vid_id}.mp4")
                if os.path.exists(filepath):
                    return filepath
                
                videoData = await loop.run_in_executor(self.executor, sync_fetch_info, f"{YTPROXY}/info/{vid_id}", headers)
                if not videoData: return None

                status = videoData.get('status')
                if status == 'success':
                    video_url = videoData['video_url']
                    return await download_with_requests(video_url, filepath, headers)
                elif status == 'error':
                    logger.error(f"API Error: {videoData.get('message', 'Unknown error')}")
                return None
            except Exception as e:
                logger.error(f"Error in video download: {str(e)}")
                return None
        
        async def song_video_dl():
            try:
                if not YT_API_KEY or not YTPROXY: return None
                headers = {"x-api-key": f"{YT_API_KEY}", "User-Agent": "Mozilla/5.0"}
                filepath = f"downloads/{title}.mp4"
                if os.path.exists(filepath): return filepath
                
                videoData = await loop.run_in_executor(self.executor, sync_fetch_info, f"{YTPROXY}/info/{vid_id}", headers)
                if videoData and videoData.get('status') == 'success':
                    return await download_with_requests(videoData['video_url'], filepath, headers)
                return None
            except Exception as e:
                logger.error(f"Error in song video download: {str(e)}")
                return None

        async def song_audio_dl():
            try:
                if not YT_API_KEY or not YTPROXY: return None
                headers = {"x-api-key": f"{YT_API_KEY}", "User-Agent": "Mozilla/5.0"}
                filepath = f"downloads/{title}.mp3"
                if os.path.exists(filepath): return filepath
                
                audioData = await loop.run_in_executor(self.executor, sync_fetch_info, f"{YTPROXY}/info/{vid_id}", headers)
                if audioData and audioData.get('status') == 'success':
                    return await download_with_requests(audioData['audio_url'], filepath, headers)
                return None
            except Exception as e:
                logger.error(f"Error in song audio download: {str(e)}")
                return None

        if songvideo:
            return await song_video_dl()
        elif songaudio:
            return await song_audio_dl()
        elif video:
            direct = True
            downloaded_file = await video_dl(vid_id)
        else:
            direct = True
            downloaded_file = await audio_dl(vid_id)
        
        return downloaded_file, direct
