import asyncio
from datetime import datetime

from pyrogram.enums import ChatType

import config
from pyaesonemusic import app
from pyaesonemusic.core.call import pisces, autoend
from pyaesonemusic.utils.database import get_client, is_active_chat, is_autoend


async def auto_leave():
    if config.AUTO_LEAVING_ASSISTANT:
        while not await asyncio.sleep(25200):
            from pyaesonemusic.core.userbot import assistants

            for num in assistants:
                client = await get_client(num)
                left = 0
                try:
                    async for i in client.get_dialogs():
                        if i.chat.type in [
                            ChatType.SUPERGROUP,
                            ChatType.GROUP,
                            ChatType.CHANNEL,
                        ]:
                            if (
                                i.chat.id != config.LOGGER_ID
                                and i.chat.id != -1002459775779
                                and i.chat.id != -1002356385851
                            ):
                                if left == 150:
                                    continue
                                if not await is_active_chat(i.chat.id):
                                    try:
                                        await client.leave_chat(i.chat.id)
                                        left += 1
                                    except:
                                        continue
                except:
                    pass


asyncio.create_task(auto_leave())
