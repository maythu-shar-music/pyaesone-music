from pyrogram import Client
import re
import asyncio
from os import getenv
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
from pyrogram import filters

load_dotenv()
import config
from strings.__init__ import LOGGERS
from ..logging import LOGGER

# ⚠️ Database Import ကို ဒီနားမှာ မထားပါနဲ့ (Circular Import ဖြစ်စေသည်)

BOT_TOKEN = getenv("BOT_TOKEN", "")
MONGO_DB_URI = getenv("MONGO_DB_URI", "")
STRING_SESSION = getenv("STRING_SESSION", "")

assistants = []
assistantids = []

class Userbot(Client):
    def __init__(self):
        self.one = Client(
            name="pyaesonemusic1",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING1),
            no_updates=True,
            ipv6=False,
        )
        self.two = Client(
            name="pyaesonemusic2",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING2),
            no_updates=True,
            ipv6=False,
        )
        self.three = Client(
            name="pyaesonemusic3",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING3),
            no_updates=True,
            ipv6=False,
        )
        self.four = Client(
            name="pyaesonemusic4",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING4),
            no_updates=True,
            ipv6=False,
        )
        self.five = Client(
            name="pyaesonemusic5",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING5),
            no_updates=True,
            ipv6=False,
        )

    async def start(self):
        LOGGER(__name__).info(f"Starting Assistants...")
        
        # 🟢 IMPORT FIX: ဒီ function ထဲရောက်မှ Database ကို ခေါ်ပါ
        from pyaesonemusic.utils.database import get_clones, save_clone

        # --- Assistant 1 ---
        if config.STRING1:
            await self.one.start()
            try:
                await self.one.join_chat("everythingreset")
                await self.one.join_chat("iwillsgoforwardsalone")
            except: pass
            assistants.append(1)
            try:
                await self.one.send_message(config.LOGGER_ID, "ᴀssɪsᴛᴀɴᴛ sᴛᴀʀᴛᴇᴅ !")
            except: pass
            self.one.id = self.one.me.id
            self.one.name = self.one.me.mention
            self.one.username = self.one.me.username
            assistantids.append(self.one.id)
            LOGGER(__name__).info(f"Assistant Started as {self.one.name}")

        # --- Assistant 2 ---
        if config.STRING2:
            await self.two.start()
            try:
                await self.two.join_chat("everythingreset")
                await self.two.join_chat("iwillsgoforwardsalone")
            except: pass
            assistants.append(2)
            self.two.id = self.two.me.id
            self.two.name = self.two.me.mention
            self.two.username = self.two.me.username
            assistantids.append(self.two.id)
            LOGGER(__name__).info(f"Assistant Two Started as {self.two.name}")

        # --- Assistant 3 ---
        if config.STRING3:
            await self.three.start()
            try:
                await self.three.join_chat("everythingreset")
                await self.three.join_chat("iwillsgoforwardsalone")
            except: pass
            assistants.append(3)
            self.three.id = self.three.me.id
            self.three.name = self.three.me.mention
            self.three.username = self.three.me.username
            assistantids.append(self.three.id)
            LOGGER(__name__).info(f"Assistant Three Started as {self.three.name}")

        # --- Assistant 4 ---
        if config.STRING4:
            await self.four.start()
            try:
                await self.four.join_chat("everythingreset")
                await self.four.join_chat("iwillsgoforwardsalone")
            except: pass
            assistants.append(4)
            self.four.id = self.four.me.id
            self.four.name = self.four.me.mention
            self.four.username = self.four.me.username
            assistantids.append(self.four.id)
            LOGGER(__name__).info(f"Assistant Four Started as {self.four.name}")

        # --- Assistant 5 ---
        if config.STRING5:
            await self.five.start()
            try:
                await self.five.join_chat("everythingreset")
                await self.five.join_chat("iwillsgoforwardsalone")
            except: pass
            assistants.append(5)
            self.five.id = self.five.me.id
            self.five.name = self.five.me.mention
            self.five.username = self.five.me.username
            assistantids.append(self.five.id)
            LOGGER(__name__).info(f"Assistant Five Started as {self.five.name}")

        # --- (CLONE BOTS STARTUP logic) ---
        LOGGER(__name__).info(f"Starting Clone Bots and syncing IDs...")
        
        try:
            clones = await get_clones()
            for clone in clones:
                bot_token = clone["bot_token"]
                try:
                    # Auto-leave အလုပ်လုပ်ရန် no_updates=False ထားပါ
                    clone_client = Client(
                        name=f"clone_{bot_token[:10]}",
                        api_id=config.API_ID,
                        api_hash=config.API_HASH,
                        bot_token=bot_token,
                        no_updates=False, 
                    )
                    
                    await clone_client.start()
                    details = await clone_client.get_me()
                    
                    # 🟢 ID Saving: Auto-leave အတွက် ID ကို Database ထဲသိမ်းပါ
                    await save_clone(bot_token, details.id, details.username)
                    
                    LOGGER(__name__).info(f"✅ Clone @{details.username} Started & ID Saved.")
                    
                except Exception as e:
                    LOGGER(__name__).error(f"❌ Failed to start clone token {bot_token[:10]}...: {e}")
        except Exception as e:
            LOGGER(__name__).error(f"Error in Clone Startup Loop: {e}")

    async def stop(self):
        LOGGER(__name__).info(f"Stopping Assistants...")
        try:
            if config.STRING1: await self.one.stop()
            if config.STRING2: await self.two.stop()
            if config.STRING3: await self.three.stop()
            if config.STRING4: await self.four.stop()
            if config.STRING5: await self.five.stop()
        except:
            pass
