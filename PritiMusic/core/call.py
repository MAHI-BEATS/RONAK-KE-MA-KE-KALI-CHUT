import asyncio
import os
import random
from datetime import datetime, timedelta
from typing import Union

from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup
from pytgcalls import PyTgCalls
from pytgcalls.exceptions import (
    AlreadyJoinedError,
    NoActiveGroupCall,
    TelegramServerError,
)
from pytgcalls.types import Update
from pytgcalls.types.input_stream import AudioPiped, AudioVideoPiped
from pytgcalls.types.input_stream.quality import HighQualityAudio, MediumQualityVideo
from pytgcalls.types.stream import StreamAudioEnded
from pyrogram.enums import ParseMode

import config
from PritiMusic import LOGGER, YouTube, app
from PritiMusic.misc import db
from PritiMusic.utils.database import (
    add_active_chat,
    add_active_video_chat,
    get_lang,
    get_loop,
    group_assistant,
    is_autoend,
    music_on,
    remove_active_chat,
    remove_active_video_chat,
    set_loop,
)
from PritiMusic.utils.exceptions import AssistantErr
from PritiMusic.utils.formatters import check_duration, seconds_to_min, speed_converter
from PritiMusic.utils.inline.play import stream_markup, telegram_markup
from PritiMusic.utils.stream.autoclear import auto_clean
from strings import get_string
from PritiMusic.utils.thumbnails import get_thumb

autoend = {}
counter = {}

FORCE_JOIN_LINKS = [
    "https://t.me/sukoon_s",
    "https://t.me/betabot_hub",
    "https://t.me/betabot_support",
]

def get_random_img(img_list):
    if img_list:
        if isinstance(img_list, list):
            return random.choice(img_list)
        return img_list
    # Local fallback option to prevent image errors
    if os.path.exists("assets/default_thumb.png"):
        return "assets/default_thumb.png"
    return "https://picsum.photos/1280/720"

# Utility function to validate external or local path image formats
def safe_image(img_path, default_config_url):
    if not img_path or str(img_path).strip().lower() == "none":
        return get_random_img(default_config_url)
    return img_path

async def _clear_(chat_id):
    db[chat_id] = []
    await remove_active_video_chat(chat_id)
    await remove_active_chat(chat_id)


class Call(PyTgCalls):
    def __init__(self):
        self.userbot1 = Client(
            name="LuckyAss1",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING1),
        )
        self.one = PyTgCalls(
            self.userbot1,
            cache_duration=100,
        )
        
        self.custom_assistants = {} 
        self.active_clients = {} 

    async def get_active_clients(self, chat_id):
        clients = []
        if chat_id in self.active_clients:
            val = self.active_clients[chat_id]
            if isinstance(val, list):
                clients.extend(val)
            else:
                clients.append(val)
        
        if not clients:
            try:
                main_ass = await group_assistant(self, chat_id)
                clients.append(main_ass)
            except Exception as e:
                LOGGER(__name__).warning(f"Failed to fetch group assistant for {chat_id}: {e}")
                clients.append(self.one)
        
        return list(set(clients))

    async def pause_stream(self, chat_id: int, assistant_type=None):
        assistants = await self.get_active_clients(chat_id)
        for assistant in assistants:
            try:
                await assistant.pause_stream(chat_id)
            except Exception as e:
                LOGGER(__name__).error(f"Stream pause failure in {chat_id}: {e}")

    async def resume_stream(self, chat_id: int, assistant_type=None):
        assistants = await self.get_active_clients(chat_id)
        for assistant in assistants:
            try:
                await assistant.resume_stream(chat_id)
            except Exception as e:
                LOGGER(__name__).error(f"Stream resume failure in {chat_id}: {e}")

    async def stop_stream(self, chat_id: int, assistant_type=None):
        assistants = await self.get_active_clients(chat_id)
        try:
            await _clear_(chat_id)
        except Exception as e:
            LOGGER(__name__).error(f"Database clearance issue in {chat_id}: {e}")
            
        for assistant in assistants:
            try:
                await assistant.leave_group_call(chat_id)
            except Exception:
                pass
        
        if chat_id in self.active_clients:
            del self.active_clients[chat_id]

    async def stop_stream_force(self, chat_id: int):
        assistants = await self.get_active_clients(chat_id)
        for assistant in assistants:
            try:
                await assistant.leave_group_call(chat_id)
            except Exception:
                pass
        
        if chat_id in self.active_clients:
            del self.active_clients[chat_id]
            
        try:
            await _clear_(chat_id)
        except Exception:
            pass

    async def speedup_stream(self, chat_id: int, file_path, speed, playing):
        if not playing or not isinstance(playing, list):
            raise AssistantErr("No playback trace found to modify speed metrics.")
            
        assistants = await self.get_active_clients(chat_id)
        
        if str(speed) != "1.0":
            base = os.path.basename(file_path)
            chatdir = os.path.join(os.getcwd(), "playback", str(speed))
            if not os.path.isdir(chatdir):
                os.makedirs(chatdir)
            out = os.path.join(chatdir, base)
            if not os.path.isfile(out):
                speed_map = {"0.5": 2.0, "0.75": 1.35, "1.5": 0.68, "2.0": 0.5}
                vs = speed_map.get(str(speed), 1.0)
                
                proc = await asyncio.create_subprocess_shell(
                    cmd=(
                        f"ffmpeg -y -i '{file_path}' "
                        f"-filter:v 'setpts={vs}*PTS' "
                        f"-filter:a 'atempo={speed}' '{out}'"
                    ),
                    stdin=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                await proc.communicate()
        else:
            out = file_path

        dur = await asyncio.get_event_loop().run_in_executor(None, check_duration, out)
        dur = int(dur)
        played, con_seconds = speed_converter(playing[0]["played"], speed)
        duration = seconds_to_min(dur)
        
        stream = (
            AudioVideoPiped(
                out,
                audio_parameters=HighQualityAudio(),
                video_parameters=MediumQualityVideo(),
                additional_ffmpeg_parameters=f"-ss {played} -to {duration}",
            )
            if playing[0].get("streamtype") == "video"
            else AudioPiped(
                out,
                audio_parameters=HighQualityAudio(),
                additional_ffmpeg_parameters=f"-ss {played} -to {duration}",
            )
        )
        
        if chat_id in db and db[chat_id] and str(db[chat_id][0]["file"]) == str(file_path):
            for assistant in assistants:
                try:
                    await assistant.change_stream(chat_id, stream)
                except Exception as e:
                    LOGGER(__name__).error(f"FFmpeg stream switch failure: {e}")
        else:
            raise AssistantErr("Queue structure updated mid-process.")

        # FIXED: Safe database manipulation to avoid IndexError
        if chat_id in db and db[chat_id] and len(db[chat_id]) > 0 and str(db[chat_id][0]["file"]) == str(file_path):
            exis = db[chat_id][0].get("old_dur")
            if not exis:
                db[chat_id][0]["old_dur"] = db[chat_id][0]["dur"]
                db[chat_id][0]["old_second"] = db[chat_id][0]["seconds"]
            db[chat_id][0]["played"] = con_seconds
            db[chat_id][0]["dur"] = duration
            db[chat_id][0]["seconds"] = dur
            db[chat_id][0]["speed_path"] = out
            db[chat_id][0]["speed"] = speed

    async def skip_stream(
        self,
        chat_id: int,
        link: str,
        video: Union[bool, str] = None,
        image: Union[bool, str] = None,
        assistant_type=None 
    ):
        assistants = await self.get_active_clients(chat_id)
        stream = (
            AudioVideoPiped(
                link,
                audio_parameters=HighQualityAudio(),
                video_parameters=MediumQualityVideo(),
            )
            if video
            else AudioPiped(link, audio_parameters=HighQualityAudio())
        )
            
        for assistant in assistants:
            try:
                await assistant.change_stream(chat_id, stream)
            except Exception as e:
                LOGGER(__name__).error(f"Skip track runtime fault: {e}")

    async def seek_stream(self, chat_id, file_path, to_seek, duration, mode):
        assistants = await self.get_active_clients(chat_id)
        stream = (
            AudioVideoPiped(
                file_path,
                audio_parameters=HighQualityAudio(),
                video_parameters=MediumQualityVideo(),
                additional_ffmpeg_parameters=f"-ss {to_seek} -to {duration}",
            )
            if mode == "video"
            else AudioPiped(
                file_path,
                audio_parameters=HighQualityAudio(),
                additional_ffmpeg_parameters=f"-ss {to_seek} -to {duration}",
            )
        )
        for assistant in assistants:
            try:
                await assistant.change_stream
