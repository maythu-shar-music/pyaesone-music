import asyncio
from pyrogram import Client, errors, filters
from pyrogram.enums import ChatMemberStatus, ParseMode

import config
from ..logging import LOGGER

# ⚠️ Database Import ကို ဒီနားမှာ မထားပါနဲ့ (Circular Import ဖြစ်စေသည်)

class pisces(Client):
    def __init__(self):
        LOGGER(__name__).info(f"Starting Bot...")
        super().__init__(
            name="pyaesonemusic",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
            in_memory=True,
            max_concurrent_transmissions=7,
        )

    async def start(self):
        await super().start()
        self.id = self.me.id
        self.name = self.me.first_name + " " + (self.me.last_name or "")
        self.username = self.me.username
        self.mention = self.me.mention

        # --- (၁) AUTO-LEAVE LOGIC (Group တစ်ခု Bot တစ်ကောင်သာ) ---
        @self.on_message(filters.group & filters.new_chat_members)
        async def auto_leave_handler(client, message):
            for member in message.new_chat_members:
                if member.is_bot:
                    try:
                        # 🟢 IMPORT FIX: ဒီနေရာမှာမှ Import လုပ်ပါ
                        from pyaesonemusic.utils.database import is_clone_bot
                        
                        # ဝင်လာသူသည် Main Bot သို့မဟုတ် Clone Bot ဖြစ်ပါက
                        if member.id == config.BOT_ID or await is_clone_bot(member.id):
                            
                            # ဝင်လာသူသည် လက်ရှိ Bot (Me) မဟုတ်ပါက (တခြားတစ်ကောင် ဝင်လာခြင်း)
                            if member.id != client.me.id:
                                await message.reply_text(
                                    f"🤖 **Conflict Detected:** @{member.username} ဝင်လာသောကြောင့် "
                                    f"ကျွန်တော် @{client.me.username} သည် ဤ Group မှ ထွက်ခွာပါမည်။"
                                )
                                # အဟောင်းရှိနေသော Bot က အလိုအလျောက် ထွက်ခွာသွားခြင်း
                                await client.leave_chat(message.chat.id)
                                break 
                    except Exception as e:
                        LOGGER(__name__).error(f"Auto-Leave Error: {e}")

        try:
            await self.send_message(
                chat_id=config.LOGGER_ID,
                text=f"<u><b>» {self.mention} ʙᴏᴛ sᴛᴀʀᴛᴇᴅ :</b><u>\n\nɪᴅ : <code>{self.id}</code>\nɴᴀᴍᴇ : {self.name}\nᴜsᴇʀɴᴀᴍᴇ : @{self.username}",
            )
        except (errors.ChannelInvalid, errors.PeerIdInvalid):
            LOGGER(__name__).error("Bot has failed to access the log group/channel.")
        except Exception as ex:
            LOGGER(__name__).error(f"Bot has failed to access the log group/channel.\n  Reason : {type(ex).__name__}.")

        LOGGER(__name__).info(f"Music Bot Started as {self.name}")

    async def stop(self):
        await super().stop()

    # --- (၃) CLEAN MODE & OVERRIDES ---
    async def add_to_clean(self, chat_id, message_id):
        try:
            if chat_id != config.LOGGER_ID:
                # 🟢 IMPORT FIX: ဒီနေရာမှာမှ Import လုပ်ပါ
                from pyaesonemusic.utils.database import add_clean_message
                await add_clean_message(chat_id, message_id)
        except:
            pass

    async def send_message(self, chat_id, text, *args, **kwargs):
        message = await super().send_message(chat_id, text, *args, **kwargs)
        await self.add_to_clean(chat_id, message.id)
        return message

    async def send_photo(self, chat_id, photo, *args, **kwargs):
        message = await super().send_photo(chat_id, photo, *args, **kwargs)
        await self.add_to_clean(chat_id, message.id)
        return message

    async def send_video(self, chat_id, video, *args, **kwargs):
        message = await super().send_video(chat_id, video, *args, **kwargs)
        await self.add_to_clean(chat_id, message.id)
        return message
