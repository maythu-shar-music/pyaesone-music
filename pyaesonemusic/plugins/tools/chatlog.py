import random
from pyrogram import Client
from pyrogram.types import Message
from pyrogram import filters
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    InputMediaVideo,
    Message,
)
from config import LOGGER_ID as LOG_GROUP_ID
from pyaesonemusic import app
from pyaesonemusic.core.userbot import Userbot
from pyaesonemusic.utils.database import delete_served_chat
from pyaesonemusic.utils.database import get_assistant


photo = [
    "https://files.catbox.moe/dul3q2.jpg",
    "https://files.catbox.moe/1ltpd1.jpg",
    "https://files.catbox.moe/kjsjsp.jpg",
]


@app.on_message(filters.new_chat_members, group=2)
async def join_watcher(_, message):
    try:
        userbot = await get_assistant(message.chat.id)
        chat = message.chat
        for members in message.new_chat_members:
            if members.id == app.id:
                count = await app.get_chat_members_count(chat.id)
                username = (
                    message.chat.username if message.chat.username else "𝐏ʀɪᴠᴀᴛᴇ 𝐆ʀᴏᴜᴘ"
                )
                msg = (
                    f"**‣ ᴍᴜꜱɪᴄ ʙᴏᴛ ᴀᴅᴅ ɪɴ ᴀ #ɴᴇᴡ_ɢʀᴏᴜᴘ**\n\n"
                    f"**‣ ᴄʜᴀᴛ ɴᴀᴍᴇ:** `{message.chat.title}`\n"
                    f"**‣ ᴄʜᴀᴛ ɪᴅ:** `{message.chat.id}`\n"
                    f"**‣ ᴄʜᴀᴛ ᴜꜱᴇʀɴᴀᴍᴇ:** @{username}\n"
                    f"**‣ ɢʀᴏᴜᴘ ᴍᴇᴍʙᴇʀꜱ:** `{count}`\n"
                    f"**‣ ᴀᴅᴅ ʙʏ:** `{message.from_user.mention}`"
                )
                await app.send_photo(
                    LOGGER_ID,
                    photo=random.choice(photo),
                    caption=msg,
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    f"ᴀᴅᴅᴇᴅ ʙʏ",
                                    url=f"tg://openmessage?user_id={message.from_user.id}",
                                )
                            ]
                        ]
                    ),
                )
                await userbot.join_chat(f"{username}")
    except Exception as e:
        print(f"Error: {e}")
