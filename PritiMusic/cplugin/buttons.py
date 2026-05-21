import math
from pyrogram.types import InlineKeyboardButton
from PritiMusic.utils.formatters import time_to_seconds
import config

# ✅ यहाँ हमने अपनी नई फाइल से इसे इम्पोर्ट कर लिया
from PritiMusic.utils.inline.button_style import ButtonStyle, styled_button 

def track_markup(_, videoid, user_id, channel, fplay):
    buttons = [
        [
            styled_button(_["P_B_1"], callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}", style=ButtonStyle.PRIMARY),
            styled_button(_["P_B_2"], callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}", style=ButtonStyle.PRIMARY),
        ],
        [
            styled_button(_["CLOSE_BUTTON"], callback_data=f"forceclose {videoid}|{user_id}", style=ButtonStyle.DANGER)
        ],
    ]
    return buttons

def stream_markup_timer(_, chat_id, played, dur):
    played_sec = time_to_seconds(played)
    duration_sec = time_to_seconds(dur)
    percentage = (played_sec / duration_sec) * 100
    umm = math.floor(percentage)
    
    if 0 <= umm <= 10: bar = "◉—————————"
    elif 10 < umm <= 20: bar = "—◉————————"
    elif 20 < umm <= 30: bar = "——◉———————"
    elif 30 < umm <= 40: bar = "———◉——————"
    elif 40 < umm <= 50: bar = "————◉—————"
    elif 50 < umm <= 60: bar = "—————◉————"
    elif 60 < umm <= 70: bar = "——————◉———"
    elif 70 < umm <= 80: bar = "———————◉——"
    elif 80 < umm <= 95: bar = "————————◉—"
    else: bar = "—————————◉"
    
    buttons = [
        [InlineKeyboardButton(text=f"{played} {bar} {dur}", callback_data="GetTimer")], # Progress bar without emoji
        [
            styled_button("▷", callback_data=f"ADMIN Resume|{chat_id}", style=ButtonStyle.SUCCESS),
            styled_button("II", callback_data=f"ADMIN Pause|{chat_id}", style=ButtonStyle.WARNING),
            styled_button("↻", callback_data=f"ADMIN Replay|{chat_id}", style=ButtonStyle.PRIMARY),
            styled_button("‣‣I", callback_data=f"ADMIN Skip|{chat_id}", style=ButtonStyle.PRIMARY),
            styled_button("▢", callback_data=f"ADMIN Stop|{chat_id}", style=ButtonStyle.DANGER),
        ],
        [styled_button("CLONE NOW", url="https://t.me/clone_MUSICrobot", style=ButtonStyle.SUCCESS)],
        [styled_button(_["CLOSE_BUTTON"], callback_data="close", style=ButtonStyle.DANGER)]
    ]
    return buttons

def stream_markup(_, chat_id):
    buttons = [
        [
            styled_button("▷", callback_data=f"ADMIN Resume|{chat_id}", style=ButtonStyle.SUCCESS),
            styled_button("II", callback_data=f"ADMIN Pause|{chat_id}", style=ButtonStyle.WARNING),
            styled_button("↻", callback_data=f"ADMIN Replay|{chat_id}", style=ButtonStyle.PRIMARY),
            styled_button("‣‣I", callback_data=f"ADMIN Skip|{chat_id}", style=ButtonStyle.PRIMARY),
            styled_button("▢", callback_data=f"ADMIN Stop|{chat_id}", style=ButtonStyle.DANGER),
        ],
        [styled_button("CLONE NOW", url="https://t.me/clone_MUSICrobot", style=ButtonStyle.SUCCESS)],
        [styled_button(_["CLOSE_BUTTON"], callback_data="close", style=ButtonStyle.DANGER)]
    ]
    return buttons

def playlist_markup(_, videoid, user_id, ptype, channel, fplay):
    buttons = [
        [
            styled_button(_["P_B_1"], callback_data=f"LuckyPlaylists {videoid}|{user_id}|{ptype}|a|{channel}|{fplay}", style=ButtonStyle.PRIMARY),
            styled_button(_["P_B_2"], callback_data=f"LuckyPlaylists {videoid}|{user_id}|{ptype}|v|{channel}|{fplay}", style=ButtonStyle.PRIMARY),
        ],
        [styled_button(_["CLOSE_BUTTON"], callback_data=f"forceclose {videoid}|{user_id}", style=ButtonStyle.DANGER)],
    ]
    return buttons

def livestream_markup(_, videoid, user_id, mode, channel, fplay):
    buttons = [
        [styled_button(_["P_B_3"], callback_data=f"LiveStream {videoid}|{user_id}|{mode}|{channel}|{fplay}", style=ButtonStyle.PRIMARY)],
        [styled_button(_["CLOSE_BUTTON"], callback_data=f"forceclose {videoid}|{user_id}", style=ButtonStyle.DANGER)],
    ]
    return buttons

def slider_markup(_, videoid, user_id, query, query_type, channel, fplay):
    query = f"{query[:20]}"
    buttons = [
        [
            styled_button(_["P_B_1"], callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}", style=ButtonStyle.PRIMARY),
            styled_button(_["P_B_2"], callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}", style=ButtonStyle.PRIMARY),
        ],
        [
            styled_button("◁", callback_data=f"slider B|{query_type}|{query}|{user_id}|{channel}|{fplay}", style=ButtonStyle.PRIMARY),
            styled_button(_["CLOSE_BUTTON"], callback_data=f"forceclose {query}|{user_id}", style=ButtonStyle.DANGER),
            styled_button("▷", callback_data=f"slider F|{query_type}|{query}|{user_id}|{channel}|{fplay}", style=ButtonStyle.PRIMARY),
        ],
        [styled_button("CLONE NOW", url="https://t.me/clone_MUSICrobot", style=ButtonStyle.SUCCESS)],
    ]
    return buttons

def telegram_markup(_, chat_id):
    buttons = [
        [
            styled_button("Next", callback_data=f"PanelMarkup None|{chat_id}", style=ButtonStyle.PRIMARY),
            styled_button(_["CLOSEMENU_BUTTON"], callback_data="close", style=ButtonStyle.DANGER),
        ],
    ]
    return buttons

def queue_markup(_, videoid, chat_id, bot_username):
    buttons = [
        [styled_button(_["S_B_3"], url=f"https://t.me/{bot_username}?startgroup=true", style=ButtonStyle.SUCCESS)],
        [
            styled_button("ᴘᴀᴜsᴇ", callback_data=f"ADMIN Pause|{chat_id}", style=ButtonStyle.WARNING),
            styled_button("sᴛᴏᴘ", callback_data=f"ADMIN Stop|{chat_id}", style=ButtonStyle.DANGER),
            styled_button("sᴋɪᴘ", callback_data=f"ADMIN Skip|{chat_id}", style=ButtonStyle.PRIMARY),
        ],
        [
            styled_button("ʀᴇsᴜᴍᴇ", callback_data=f"ADMIN Resume|{chat_id}", style=ButtonStyle.SUCCESS),
            styled_button("ʀᴇᴘʟᴀʏ", callback_data=f"ADMIN Replay|{chat_id}", style=ButtonStyle.PRIMARY),
        ],
        [styled_button("ᴍᴏʀᴇ", callback_data=f"PanelMarkup None|{chat_id}", style=ButtonStyle.BACK)],
        [styled_button("CLONE NOW", url="https://t.me/clone_MUSICrobot", style=ButtonStyle.SUCCESS)],
    ]
    return buttons

def stream_markup2(_, chat_id, bot_username):
    buttons = [
        [styled_button(_["S_B_3"], url=f"https://t.me/{bot_username}?startgroup=true", style=ButtonStyle.SUCCESS)],
        [
            styled_button("▷", callback_data=f"ADMIN Resume|{chat_id}", style=ButtonStyle.SUCCESS),
            styled_button("II", callback_data=f"ADMIN Pause|{chat_id}", style=ButtonStyle.WARNING),
            styled_button("↻", callback_data=f"ADMIN Replay|{chat_id}", style=ButtonStyle.PRIMARY),
            styled_button("‣‣I", callback_data=f"ADMIN Skip|{chat_id}", style=ButtonStyle.PRIMARY),
            styled_button("▢", callback_data=f"ADMIN Stop|{chat_id}", style=ButtonStyle.DANGER),
        ],
        [styled_button("CLONE NOW", url="https://t.me/clone_MUSICrobot", style=ButtonStyle.SUCCESS)],
        [styled_button(_["CLOSEMENU_BUTTON"], callback_data="close", style=ButtonStyle.DANGER)],
    ]
    return buttons

def stream_markup_timer2(_, chat_id, played, dur):
    played_sec = time_to_seconds(played)
    duration_sec = time_to_seconds(dur)
    percentage = (played_sec / duration_sec) * 100
    umm = math.floor(percentage)
    
    if 0 <= umm <= 10: bar = "◉—————————"
    elif 10 < umm <= 20: bar = "—◉————————"
    elif 20 < umm <= 30: bar = "——◉———————"
    elif 30 < umm <= 40: bar = "———◉——————"
    elif 40 < umm <= 50: bar = "————◉—————"
    elif 50 < umm <= 60: bar = "—————◉————"
    elif 60 < umm <= 70: bar = "——————◉———"
    elif 70 < umm <= 80: bar = "———————◉——"
    elif 80 < umm <= 95: bar = "————————◉—"
    else: bar = "—————————◉"
    
    buttons = [
        [InlineKeyboardButton(text=f"{played} {bar} {dur}", callback_data="GetTimer")],
        [
            styled_button("▷", callback_data=f"ADMIN Resume|{chat_id}", style=ButtonStyle.SUCCESS),
            styled_button("II", callback_data=f"ADMIN Pause|{chat_id}", style=ButtonStyle.WARNING),
            styled_button("↻", callback_data=f"ADMIN Replay|{chat_id}", style=ButtonStyle.PRIMARY),
            styled_button("‣‣I", callback_data=f"ADMIN Skip|{chat_id}", style=ButtonStyle.PRIMARY),
            styled_button("▢", callback_data=f"ADMIN Stop|{chat_id}", style=ButtonStyle.DANGER),
        ],
        [styled_button("CLONE NOW", url="https://t.me/clone_MUSICrobot", style=ButtonStyle.SUCCESS)],
        [styled_button(_["CLOSEMENU_BUTTON"], callback_data="close", style=ButtonStyle.DANGER)],
    ]
    return buttons

def panel_markup_1(_, videoid, chat_id, bot_username):
    buttons = [
        [styled_button(_["S_B_3"], url=f"https://t.me/{bot_username}?startgroup=true", style=ButtonStyle.SUCCESS)],
        [
            styled_button("sᴜғғʟᴇ", callback_data=f"ADMIN Shuffle|{chat_id}", style=ButtonStyle.PRIMARY),
            styled_button("ʟᴏᴏᴘ", callback_data=f"ADMIN Loop|{chat_id}", style=ButtonStyle.PRIMARY),
        ],
        [
            styled_button("-10 sᴇᴄ", callback_data=f"ADMIN 1|{chat_id}", style=ButtonStyle.PRIMARY),
            styled_button("+10 sᴇᴄ", callback_data=f"ADMIN 2|{chat_id}", style=ButtonStyle.PRIMARY),
        ],
        [
            styled_button("HOME", callback_data=f"Pages Back|2|{videoid}|{chat_id}", style=ButtonStyle.BACK),
            styled_button("NEXT", callback_data=f"Pages Forw|2|{videoid}|{chat_id}", style=ButtonStyle.BACK),
        ],
    ]
    return buttons

def panel_markup_2(_, videoid, chat_id, bot_username):
    buttons = [
        [styled_button(_["S_B_3"], url=f"https://t.me/{bot_username}?startgroup=true", style=ButtonStyle.SUCCESS)],
        [
            styled_button("0.5x", callback_data=f"SpeedUP {chat_id}|0.5", style=ButtonStyle.PRIMARY),
            styled_button("0.75x", callback_data=f"SpeedUP {chat_id}|0.75", style=ButtonStyle.PRIMARY),
            styled_button("1.0x", callback_data=f"SpeedUP {chat_id}|1.0", style=ButtonStyle.SUCCESS), # Default speed is SUCCESS
        ],
        [
            styled_button("1.5x", callback_data=f"SpeedUP {chat_id}|1.5", style=ButtonStyle.PRIMARY),
            styled_button("2.0x", callback_data=f"SpeedUP {chat_id}|2.0", style=ButtonStyle.PRIMARY),
        ],
        [styled_button("CLONE NOW", url="https://t.me/clone_MUSICrobot", style=ButtonStyle.SUCCESS)],
        [styled_button("BACK", callback_data=f"Pages Back|1|{videoid}|{chat_id}", style=ButtonStyle.BACK)],
    ]
    return buttons

def panel_markup_3(_, videoid, chat_id):
    buttons = [
        [
            styled_button("0.5x", callback_data=f"SpeedUP {chat_id}|0.5", style=ButtonStyle.PRIMARY),
            styled_button("0.75x", callback_data=f"SpeedUP {chat_id}|0.75", style=ButtonStyle.PRIMARY),
            styled_button("1.0x", callback_data=f"SpeedUP {chat_id}|1.0", style=ButtonStyle.SUCCESS),
        ],
        [
            styled_button("1.5x", callback_data=f"SpeedUP {chat_id}|1.5", style=ButtonStyle.PRIMARY),
            styled_button("2.0x", callback_data=f"SpeedUP {chat_id}|2.0", style=ButtonStyle.PRIMARY),
        ],
        [styled_button("CLONE NOW", url="https://t.me/clone_MUSICrobot", style=ButtonStyle.SUCCESS)],
        [styled_button("BACK", callback_data=f"Pages Back|2|{videoid}|{chat_id}", style=ButtonStyle.BACK)],
    ]
    return buttons

def panel_markup_4(_, vidid, chat_id, played, dur):
    played_sec = time_to_seconds(played)
    duration_sec = time_to_seconds(dur)
    percentage = (played_sec / duration_sec) * 100
    umm = math.floor(percentage)
    
    if 0 <= umm <= 10: bar = "◉—————————"
    elif 10 < umm <= 20: bar = "—◉————————"
    elif 20 < umm <= 30: bar = "——◉———————"
    elif 30 < umm <= 40: bar = "———◉——————"
    elif 40 < umm <= 50: bar = "————◉—————"
    elif 50 < umm <= 60: bar = "—————◉————"
    elif 60 < umm <= 70: bar = "——————◉———"
    elif 70 < umm <= 80: bar = "———————◉——"
    elif 80 < umm <= 95: bar = "————————◉—"
    else: bar = "—————————◉"
    
    buttons = [
        [InlineKeyboardButton(text=f"{played} {bar} {dur}", callback_data="GetTimer")],
        [
            styled_button("ᴘᴀᴜsᴇ", callback_data=f"ADMIN Pause|{chat_id}", style=ButtonStyle.WARNING),
            styled_button("sᴛᴏᴘ", callback_data=f"ADMIN Stop|{chat_id}", style=ButtonStyle.DANGER),
            styled_button("sᴋɪᴘ", callback_data=f"ADMIN Skip|{chat_id}", style=ButtonStyle.PRIMARY),
        ],
        [
            styled_button("ʀᴇsᴜᴍᴇ", callback_data=f"ADMIN Resume|{chat_id}", style=ButtonStyle.SUCCESS),
            styled_button("ʀᴇᴘʟᴀʏ", callback_data=f"ADMIN Replay|{chat_id}", style=ButtonStyle.PRIMARY),
        ],
        [styled_button("CLONE NOW", url="https://t.me/clone_MUSICrobot", style=ButtonStyle.SUCCESS)],
        [styled_button("HOME", callback_data=f"MainMarkup {vidid}|{chat_id}", style=ButtonStyle.BACK)],
    ]
    return buttons

def panel_markup_5(_, videoid, chat_id, bot_username):
    buttons = [
        [styled_button(_["S_B_3"], url=f"https://t.me/{bot_username}?startgroup=true", style=ButtonStyle.SUCCESS)],
        [
            styled_button("ᴘᴀᴜsᴇ", callback_data=f"ADMIN Pause|{chat_id}", style=ButtonStyle.WARNING),
            styled_button("sᴛᴏᴘ", callback_data=f"ADMIN Stop|{chat_id}", style=ButtonStyle.DANGER),
            styled_button("sᴋɪᴘ", callback_data=f"ADMIN Skip|{chat_id}", style=ButtonStyle.PRIMARY),
        ],
        [
            styled_button("ʀᴇsᴜᴍᴇ", callback_data=f"ADMIN Resume|{chat_id}", style=ButtonStyle.SUCCESS),
            styled_button("ʀᴇᴘʟᴀʏ", callback_data=f"ADMIN Replay|{chat_id}", style=ButtonStyle.PRIMARY),
        ],
        [
            styled_button("HOME", callback_data=f"MainMarkup {videoid}|{chat_id}", style=ButtonStyle.BACK),
            styled_button("NEXT", callback_data=f"Pages Forw|1|{videoid}|{chat_id}", style=ButtonStyle.BACK),
        ],
    ]
    return buttons

def panel_markup_clone(_, vidid, chat_id):
    buttons = [
        [
            styled_button("▷", callback_data=f"ADMIN Resume|{chat_id}", style=ButtonStyle.SUCCESS),
            styled_button("II", callback_data=f"ADMIN Pause|{chat_id}", style=ButtonStyle.WARNING),
            styled_button("‣‣I", callback_data=f"ADMIN Skip|{chat_id}", style=ButtonStyle.PRIMARY),
            styled_button("▢", callback_data=f"ADMIN Stop|{chat_id}", style=ButtonStyle.DANGER),
        ],
        [styled_button("CLONE NOW", url="https://t.me/clone_MUSICrobot", style=ButtonStyle.SUCCESS)],
        [styled_button(_["CLOSE_BUTTON"], callback_data="close", style=ButtonStyle.DANGER)]
    ]
    return buttons
