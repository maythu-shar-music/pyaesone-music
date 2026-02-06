import re
import logging
import traceback
import os
import shutil
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import AccessTokenInvalid

from config import API_ID, API_HASH, OWNER_ID
from pyaesonemusic import app
from pyaesonemusic.utils.database import get_assistant

# Clone Bot များကို ယာယီမှတ်ထားရန်
CLONES = set()

# --- (၁) AUTO CHECK MAIN BOT FUNCTION ---
async def auto_check_main_bot(clone_client):
    """Clone Bot ရှိသော Group များတွင် Main Bot ရှိမရှိ စစ်ဆေးပြီး မရှိရင် ထည့်သည်"""
    try:
        if not app.me:
            await app.get_me()
        main_bot_username = app.me.username
        main_bot_id = app.me.id

        # Clone Bot ရောက်နေသော Chat များကို တန်းစီစစ်ဆေးမည်
        async for dialog in clone_client.get_dialogs():
            # Group နှင့် Supergroup များကိုသာ စစ်မည်
            if dialog.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
                chat_id = dialog.chat.id
                try:
                    # Main Bot ရှိမရှိ စစ်ဆေးခြင်း
                    await clone_client.get_chat_member(chat_id, main_bot_id)
                except UserNotParticipant:
                    # Main Bot မရှိရင် Assistant ဖြင့် ဆွဲထည့်မည်
                    try:
                        userbot = await get_assistant(chat_id)
                        await userbot.add_chat_members(chat_id, main_bot_username)
                        # ထည့်ပြီးကြောင်း Log ပြမည် (Optional)
                        # print(f"Added Main Bot to {dialog.chat.title}")
                    except Exception:
                        pass # Assistant Admin မဟုတ်လို့ ထည့်မရရင် ကျော်သွားမည်
                except Exception:
                    pass
                
                # FloodWait ရှောင်ရန် အနည်းငယ် နားမည်
                await asyncio.sleep(2)
                
    except Exception as e:
        print(f"Auto Sync Error for {clone_client.me.username}: {e}")

@app.on_message(filters.command("clone") & filters.private)
async def clone_txt(client, message: Message):
    try:
        from pyaesonemusic.utils.database import save_clone, get_clones, is_clones_active
        
        # --- (၁) SYSTEM ON/OFF CHECK ---
        if not await is_clones_active():
            return await message.reply_text("❌ Clone bot စနစ်ကို Owner မှ ယာယီပိတ်ထားပါသည်။")

        user_id = message.from_user.id
        
        # --- (၂) 3 BOTS LIMIT CHECK ---
        all_clones = await get_clones()
        # User ပိုင်တဲ့ bot တွေကို စစ်ထုတ်ခြင်း
        user_clones = [c for c in all_clones if c.get("user_id") == user_id]
        
        if len(user_clones) >= 3:
            bot_list = "\n".join([f"• @{c.get('bot_username')} (`/delclone {c.get('bot_token')}`)" for c in user_clones])
            return await message.reply_text(
                f"⚠️ **Limit Reached!**\n\n"
                f"သင်သည် Clone Bot (၃) ခုထက်ပို၍ ဖန်တီး၍မရပါ။\n"
                f"လက်ရှိသင့် Bot များမှာ -\n{bot_list}\n\n"
                f"အသစ်ပြုလုပ်လိုပါက ရှိပြီးသားတစ်ခုကို အရင်ဖျက်ပါ။"
            )

        # Token ပါမပါ စစ်ဆေးခြင်း
        if len(message.command) < 2:
            return await message.reply_text(
                "<b>Usage:</b>\n/clone [Bot Token]\n\n@BotFather ထံမှ Token ယူခဲ့ပါ။"
            )
        
        bot_token = message.text.split(None, 1)[1]
        
        # Token format စစ်ဆေးခြင်း
        if not re.match(r'^\d+:[a-zA-Z0-9_-]+$', bot_token):
            return await message.reply_text("❌ Invalid Bot Token format.")

        # ရှိပြီးသား token ဖြစ်နေလား စစ်ခြင်း (Double cloning ကာကွယ်ရန်)
        if any(c.get("bot_token") == bot_token for c in all_clones):
            return await message.reply_text("❌ ဤ Bot သည် စနစ်ထဲတွင် ရှိနှင့်နေပြီးသား ဖြစ်သည်။")

        msg = await message.reply_text("⏳ 𝘾𝙧𝙚𝙖𝙩𝙞𝙣𝙜 𝙮𝙤𝙪𝙧 𝙗𝙤𝙩. 𝙋𝙡𝙚𝙖𝙨𝙚 𝙬𝙖𝙞𝙩...")

        try:
            ai = Client(
                name=f"clone_{bot_token.split(':')[0]}",
                api_id=API_ID,
                api_hash=API_HASH,
                bot_token=bot_token,
                plugins=dict(root="pyaesonemusic.plugins.clone_plugins"),
            )
            
            await ai.start()
            bot_info = await ai.get_me()
            username = bot_info.username
            
            await save_clone(bot_token, user_id, username)
            CLONES.add(bot_token)
            
            await msg.edit_text(
                f"✅ **Clone Bot Successfully Created!**\n\n"
                f"🤖 **Bot:** @{username}\n"
                f"👤 **Owner:** {message.from_user.mention}\n"
                f"🔢 **Slots:** {len(user_clones) + 1}/3\n\n"
                f"Bot ကို Group ထဲထည့်ပြီး Admin ပေးလိုက်ပါက သီချင်းဖွင့်နိုင်ပါပြီ။"
            )
            
        except AccessTokenInvalid:
            await msg.edit_text("❌ Token မှားယွင်းနေပါသည်။")
        except Exception as e:
            await msg.edit_text(f"❌ Error: {e}")
        
    except Exception as e:
        await message.reply_text(f"❌ Unexpected error: {e}")

@app.on_message(filters.command("delclone") & filters.private)
async def delete_clone_bot(client, message: Message):
    try:
        from pyaesonemusic.utils.database import delete_clone, get_clone_by_user
        
        token = None
        if len(message.command) >= 2:
            token = message.text.split(None, 1)[1]
        else:
            user_clone = await get_clone_by_user(message.from_user.id)
            if user_clone:
                token = user_clone.get("bot_token")
            else:
                return await message.reply_text("ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴀ ᴄʟᴏɴᴇ ʙᴏᴛ ᴛᴏ ᴅᴇʟᴇᴛᴇ.")

        if token:
            await delete_clone(token)
            if token in CLONES:
                CLONES.remove(token)
            await message.reply_text("✅ ᴄʟᴏɴᴇ ʙᴏᴛ ʜᴀꜱ ʙᴇᴇɴ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴜɴɪɴꜱᴛᴀʟʟᴇᴅ.")
        else:
            await message.reply_text("❌ ɪɴᴠᴀʟɪᴅ ᴛᴏᴋᴇɴ ᴏʀ ɴᴏ ᴄʟᴏɴᴇ ʙᴏᴛ ꜰᴏᴜɴᴅ.")
        
    except Exception as e:
        await message.reply_text(f"ᴇʀʀᴏʀ : {e}")

# --- (၁) OWNER ONLY: Clone Bot အရေအတွက် ကြည့်ခြင်း ---
@app.on_message(filters.command("checkbot") & filters.user(OWNER_ID))
async def total_clones_stats(client, message: Message):
    try:
        from pyaesonemusic.utils.database import get_clones
        clones = await get_clones()
        
        total = len(clones)
        text = f"📊 <b>𝗖𝗹𝗼𝗻𝗲 𝗕𝗼𝘁 𝗦𝘁𝗮𝘁𝗶𝘀𝘁𝗶𝗰𝘀</b>\n\n"
        text += f"🤖 <b>𝗧𝗼𝘁𝗮𝗹 𝗖𝗹𝗼𝗻𝗲𝘀 : </b> {total}\n\n"
        
        if total > 0:
            text += "<b>𝗕𝗼𝘁 𝗨𝘀𝗲𝗿𝗻𝗮𝗺𝗲𝘀 : </b>\n"
            for count, clone in enumerate(clones, 1):
                username = clone.get("bot_username", "Unknown")
                text += f"{count}. @{username}\n"
        
        await message.reply_text(text)
    except Exception as e:
        await message.reply_text(f"Error: {e}")

# --- (၂) OWNER ONLY: Clone Bot အားလုံးကို ဖျက်ခြင်း ---
@app.on_message(filters.command("delallclones") & filters.user(OWNER_ID))
async def delete_all_clones_func(client, message: Message):
    try:
        from pyaesonemusic.utils.database import remove_all_clones, get_clones
        
        # Confirm လုပ်ခိုင်းခြင်း
        if len(message.command) < 2 or message.text.split()[1] != "confirm":
            return await message.reply_text(
                "𝗪𝗮𝗿𝗻𝗶𝗻𝗴\n"
                "𝗔𝗿𝗲 𝘆𝗼𝘂 𝘀𝘂𝗿𝗲 𝘆𝗼𝘂 𝘄𝗮𝗻𝘁 𝘁𝗼 𝗱𝗲𝗹𝗲𝘁𝗲 𝗮𝗹𝗹 𝗖𝗹𝗼𝗻𝗲 𝗕𝗼𝘁𝘀.\n"
                "𝙄𝙛 𝙮𝙤𝙪 𝙖𝙧𝙚 𝙨𝙪𝙧𝙚, 𝙩𝙮𝙥𝙚 𝙩𝙝𝙚 𝙛𝙤𝙡𝙡𝙤𝙬𝙞𝙣𝙜 :\n"
                "<code>/delallclones confirm</code>"
            )
            
        msg = await message.reply_text("♻️ <b>𝘼𝙡𝙡 𝘾𝙡𝙤𝙣𝙚 𝘽𝙤𝙩𝙨 𝙖𝙧𝙚 𝙗𝙚𝙞𝙣𝙜 𝙙𝙚𝙡𝙚𝙩𝙚𝙙...</b>")
        
        # Database ရှင်းလင်းခြင်း
        await remove_all_clones()
        CLONES.clear()
        
        await msg.edit_text("✅ <b>𝘼𝙡𝙡 𝘾𝙡𝙤𝙣𝙚 𝘽𝙤𝙩𝙨 𝙝𝙖𝙫𝙚 𝙗𝙚𝙚𝙣 𝙨𝙪𝙘𝙘𝙚𝙨𝙨𝙛𝙪𝙡𝙡𝙮 𝙙𝙚𝙡𝙚𝙩𝙚𝙙 𝙛𝙧𝙤𝙢 𝙩𝙝𝙚 𝘿𝙖𝙩𝙖𝙗𝙖𝙨𝙚.</b>\n\n𝙍𝙚𝙨𝙩𝙖𝙧𝙩 𝙩𝙝𝙚 𝙗𝙤𝙩 𝙛𝙤𝙧 𝙩𝙝𝙚 𝙚𝙛𝙛𝙚𝙘𝙩 𝙩𝙤 𝙩𝙖𝙠𝙚 𝙚𝙛𝙛𝙚𝙘𝙩. (/reboot)")
        
    except Exception as e:
        await message.reply_text(f"Error: {e}")

async def restart_clones():
    try:
        from pyaesonemusic.utils.database import get_clones
        clones = await get_clones()
        
        if not clones:
            return
        
        print(f"Total Clones Found: {len(clones)}")
        
        for clone in clones:
            token = clone["bot_token"]
            try:
                ai = Client(
                    name=token,
                    api_id=API_ID,
                    api_hash=API_HASH,
                    bot_token=token,
                    plugins=dict(root="pyaesonemusic.plugins.piscesplugins"),
                )
                await ai.start()
                print(f"𝗦𝘁𝗮𝗿𝘁𝗲𝗱 𝗖𝗹𝗼𝗻𝗲 : @{clone['bot_username']}")
                CLONES.add(token)
            except Exception as e:
                print(f"Failed to start clone {token}: {e}")
    except ImportError:
        print("Database module loading error inside restart_clones")
    except Exception as e:
        print(f"Error in restart_clones: {e}")

@app.on_message(filters.command("clonebot") & filters.user(OWNER_ID))
async def clone_mode_switch(client, message: Message):
    try:
        from pyaesonemusic.utils.database import set_clones_active, is_clones_active
        
        if len(message.command) != 2:
            status = await is_clones_active()
            txt = "✅ <b>Enabled</b>" if status else "❌ <b>Disabled</b>"
            return await message.reply_text(f"<b>Current Clone System Status:</b> {txt}\n\n<b>Usage:</b> <code>/clonebot [on|off]</code>")
            
        state = message.text.split(None, 1)[1].strip().lower()
        
        if state == "on" or state == "enable":
            await set_clones_active(True)
            await message.reply_text("✅ <b>𝘾𝙡𝙤𝙣𝙚 𝘽𝙤𝙩 𝙎𝙮𝙨𝙩𝙚𝙢 𝙝𝙖𝙨 𝙗𝙚𝙚𝙗 𝙖𝙘𝙩𝙞𝙫𝙖𝙩𝙚𝙙.</b>\n𝘼𝙡𝙡 𝘾𝙡𝙤𝙣𝙚 𝘽𝙤𝙩𝙨 𝙬𝙞𝙡𝙡 𝙧𝙚𝙨𝙪𝙢𝙚 𝙣𝙤𝙧𝙢𝙖𝙡 𝙤𝙥𝙚𝙧𝙖𝙩𝙞𝙤𝙣.")
            
        elif state == "off" or state == "disable":
            await set_clones_active(False)
            await message.reply_text("❌ <b>𝙏𝙝𝙚 𝘾𝙡𝙤𝙣𝙚 𝘽𝙤𝙩 𝙎𝙮𝙨𝙩𝙚𝙢 𝙝𝙖𝙨 𝙗𝙚𝙚𝙣 𝙙𝙞𝙨𝙖𝙗𝙡𝙚𝙙.</b>\n𝘼𝙡𝙡 𝘾𝙡𝙤𝙣𝙚 𝘽𝙤𝙩𝙨 𝙬𝙞𝙡𝙡 𝙨𝙝𝙤𝙬 '𝙐𝙣𝙙𝙚𝙧 𝙈𝙖𝙞𝙣𝙩𝙚𝙣𝙖𝙣𝙘𝙚'.")
            
        else:
            await message.reply_text("<b>Usage:</b> <code>/clonebot [on|off]</code>")
            
    except Exception as e:
        await message.reply_text(f"Error: {e}")
