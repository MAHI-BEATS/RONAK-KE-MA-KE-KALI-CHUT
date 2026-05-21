import os
import random
from typing import Union

from pyrogram.types import InlineKeyboardMarkup
import pyrogram.errors

import config
from PritiMusic import Carbon, YouTube, app
from PritiMusic.core.call import Lucky
from PritiMusic.misc import db
from PritiMusic.utils.database import add_active_video_chat, is_active_chat
from PritiMusic.utils.exceptions import AssistantErr
from PritiMusic.utils.inline import aq_markup, close_markup, stream_markup
from PritiMusic.utils.stream.queue import put_queue, put_queue_index
from PritiMusic.utils.pastebin import LuckyBin
from PritiMusic.utils.thumbnails import get_thumb  # Thumbnail Module

# Dynamic random string image utility
def get_random_img(img_list):
    if img_list:
        if isinstance(img_list, list):
            return random.choice(img_list)
        return img_list
    return "https://files.catbox.moe/n22tbs.jpg"

async def stream(
    _,
    mystic,
    user_id,
    result,
    chat_id,
    user_name,
    original_chat_id,
    video: Union[bool, str] = None,
    streamtype: Union[bool, str] = None,
    spotify: Union[bool, str] = None,
    forceplay: Union[bool, str] = None,
):
    if not result:
        return
    if forceplay:
        try:
            await Lucky.force_stop_stream(chat_id)
        except Exception:
            pass

    if streamtype == "playlist":
        msg = f"{_['play_19']}\n\n"
        count = 0
        for search in result:
            if int(count) == config.PLAYLIST_FETCH_LIMIT:
                continue
            try:
                (
                    title,
                    duration_min,
                    duration_sec,
                    thumbnail,
                    vidid,
                ) = await YouTube.details(search, False if spotify else True)
            except Exception:
                continue
            if str(duration_min) == "None":
                continue
            if duration_sec > config.DURATION_LIMIT:
                continue
            if await is_active_chat(chat_id):
                await put_queue(
                    chat_id,
                    original_chat_id,
                    f"vid_{vidid}",
                    title,
                    duration_min,
                    user_name,
                    vidid,
                    user_id,
                    "video" if video else "audio",
                )
                try:
                    position = len(db.get(chat_id)) - 1
                except Exception:
                    position = 1
                count += 1
                msg += f"{count}. {title[:70]}\n"
                msg += f"{_['play_20']} {position}\n\n"
            else:
                if not forceplay:
                    db[chat_id] = []
                status = True if video else None
                try:
                    file_path, direct = await YouTube.download(
                        vidid, mystic, video=status, videoid=True
                    )
                except Exception:
                    raise AssistantErr(_["play_14"])
                
                # 'None' File Path Error Fix
                if not file_path or str(file_path).strip() == "None":
                    raise AssistantErr("Download failed. File path received as None.")

                await Lucky.join_call(
                    chat_id,
                    original_chat_id,
                    file_path,
                    video=status,
                    image=thumbnail,
                )
                await put_queue(
                    chat_id,
                    original_chat_id,
                    file_path if direct else f"vid_{vidid}",
                    title,
                    duration_min,
                    user_name,
                    vidid,
                    user_id,
                    "video" if video else "audio",
                    forceplay=forceplay,
                )
                
                # Await dynamic thumbnail generator securely
                try:
                    img = await get_thumb(vidid)
                except Exception:
                    img = get_random_img(config.PLAYLIST_IMG_URL)
                
                if not img: 
                    img = get_random_img(config.PLAYLIST_IMG_URL)

                button = stream_markup(_, chat_id)
                try:
                    run = await app.send_photo(
                        original_chat_id,
                        photo=img,
                        caption=_["stream_1"].format(
                            f"https://t.me/{app.username}?start=info_{vidid}",
                            title[:23],
                            duration_min,
                            user_name,
                        ),
                        reply_markup=InlineKeyboardMarkup(button),
                        has_spoiler=True
                    )
                    # IndexError Fix via Safety Checks
                    if chat_id in db and isinstance(db[chat_id], list) and len(db[chat_id]) > 0:
                        db[chat_id][0]["mystic"] = run
                        db[chat_id][0]["markup"] = "stream"
                except Exception:
                    pass

        if count == 0:
            return
        else:
            link = await LuckyBin(msg)
            lines = msg.count("\n")
            if lines >= 17:
                car = os.linesep.join(msg.split(os.linesep)[:17])
            else:
                car = msg
            carbon = await Carbon.generate(car, random.randint(100, 10000000))
            upl = close_markup(_)
            try:
                position = len(db.get(chat_id)) - 1
            except Exception:
                position = 1
            return await app.send_photo(
                original_chat_id,
                photo=carbon,
                caption=_["play_21"].format(position, link),
                reply_markup=upl,
                has_spoiler=True
            )

    elif streamtype == "youtube":
        link = result["link"]
        vidid = result["vidid"]
        title = (result["title"]).title()
        duration_min = result["duration_min"]
        thumbnail = result["thumb"]
        status = True if video else None
        try:
            file_path, direct = await YouTube.download(
                vidid, mystic, videoid=True, video=status
            )
        except Exception:
            raise AssistantErr(_["play_14"])
        
        # 'None' File Path Error Fix
        if not file_path or str(file_path).strip() == "None":
            raise AssistantErr("Download failed. File path received as None.")
        
        if await is_active_chat(chat_id):
            await put_queue(
                chat_id,
                original_chat_id,
                file_path if direct else f"vid_{vidid}",
                title,
                duration_min,
                user_name,
                vidid,
                user_id,
                "video" if video else "audio",
            )
            try:
                position = len(db.get(chat_id)) - 1
            except Exception:
                position = 1
            button = aq_markup(_, chat_id)
            await app.send_message(
                chat_id=original_chat_id,
                text=_["queue_4"].format(position, title[:27], duration_min, user_name),
                reply_markup=InlineKeyboardMarkup(button),
            )
        else:
            if not forceplay:
                db[chat_id] = []
            await Lucky.join_call(
                chat_id,
                original_chat_id,
                file_path,
                video=status,
                image=thumbnail,
            )
            await put_queue(
                chat_id,
                original_chat_id,
                file_path if direct else f"vid_{vidid}",
                title,
                duration_min,
                user_name,
                vidid,
                user_id,
                "video" if video else "audio",
                forceplay=forceplay,
            )
            
            try:
                img = await get_thumb(vidid)
            except Exception:
                img = get_random_img(config.YOUTUBE_IMG_URL)
                
            if not img: 
                img = get_random_img(config.YOUTUBE_IMG_URL)

            button = stream_markup(_, chat_id)
            try:
                run = await app.send_photo(
                    original_chat_id,
                    photo=img,
                    caption=_["stream_1"].format(
                        f"https://t.me/{app.username}?start=info_{vidid}",
                        title[:23],
                        duration_min,
                        user_name,
                    ),
                    reply_markup=InlineKeyboardMarkup(button),
                    has_spoiler=True
                )
                # IndexError Fix via Safety Checks
                if chat_id in db and isinstance(db[chat_id], list) and len(db[chat_id]) > 0:
                    db[chat_id][0]["mystic"] = run
                    db[chat_id][0]["markup"] = "stream"
            except Exception:
                pass

    elif streamtype == "soundcloud":
        file_path = result["filepath"]
        title = result["title"]
        duration_min = result["duration_min"]
        if await is_active_chat(chat_id):
            await put_queue(
                chat_id,
                original_chat_id,
                file_path,
                title,
                duration_min,
                user_name,
                streamtype,
                user_id,
                "audio",
            )
            try:
                position = len(db.get(chat_id)) - 1
            except Exception:
                position = 1
            button = aq_markup(_, chat_id)
            await app.send_message(
                chat_id=original_chat_id,
                text=_["queue_4"].format(position, title[:27], duration_min, user_name),
                reply_markup=InlineKeyboardMarkup(button),
            )
        else:
            if not forceplay:
                db[chat_id] = []
            await Lucky.join_call(chat_id, original_chat_id, file_path, video=None)
            await put_queue(
                chat_id,
                original_chat_id,
                file_path,
                title,
                duration_min,
                user_name,
                streamtype,
                user_id,
                "audio",
                forceplay=forceplay,
            )
            button = stream_markup(_, chat_id)
            try:
                run = await app.send_photo(
                    original_chat_id,
                    photo=get_random_img(config.SOUNCLOUD_IMG_URL),
                    caption=_["stream_1"].format(
                        config.SUPPORT_CHAT, title[:23], duration_min, user_name
                    ),
                    reply_markup=InlineKeyboardMarkup(button),
                    has_spoiler=True
                )
                if chat_id in db and isinstance(db[chat_id], list) and len(db[chat_id]) > 0:
                    db[chat_id][0]["mystic"] = run
                    db[chat_id][0]["markup"] = "tg"
            except Exception:
                pass

    elif streamtype == "telegram":
        file_path = result["path"]
        link = result["link"]
        title = (result["title"]).title()
        duration_min = result["dur"]
        status = True if video else None
        if await is_active_chat(chat_id):
            await put_queue(
                chat_id,
                original_chat_id,
                file_path,
                title,
                duration_min,
                user_name,
                streamtype,
                user_id,
                "video" if video else "audio",
            )
            try:
                position = len(db.get(chat_id)) - 1
            except Exception:
                position = 1
            button = aq_markup(_, chat_id)
            await app.send_message(
                chat_id=original_chat_id,
                text=_["queue_4"].format(position, title[:27], duration_min, user_name),
