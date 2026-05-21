from pyrogram.types import InlineKeyboardButton

class ButtonStyle:
    PRIMARY = "primary"
    SUCCESS = "success"
    DANGER = "danger"
    WARNING = "warning"
    BACK = "back"

def styled_button(text, callback_data=None, url=None, style=ButtonStyle.PRIMARY):
    style_map = {
        ButtonStyle.PRIMARY: "🔹",
        ButtonStyle.SUCCESS: "✅",
        ButtonStyle.DANGER: "❌",
        ButtonStyle.WARNING: "⚠️",
        ButtonStyle.BACK: "•",
    }
    
    prefix = style_map.get(style, "🔹")
    
    if style == ButtonStyle.BACK:
        clean_text = str(text).upper() 
        button_text = f"• {clean_text} •"
    else:
        button_text = f"{prefix} {text}"
        
    return InlineKeyboardButton(
        text=button_text,
        callback_data=callback_data,
        url=url
    )
