from pyrogram import filters
from pyrogram.types import Message
from pyaesonemusic import app
from pyaesonemusic.utils.database import get_assistant
from pyaesonemusic.utils.decorators import AdminRightsCheck
from config import LOG_GROUP_ID

# --- (၁) VOICE CHAT ဖွင့်ခြင်း (/startvc) ---
@app.on_message(filters.command(["startvc", "vcstart"]) & filters.group)
@AdminRightsCheck
async def start_vc(client, message: Message, _, chat_id):
    # Assistant Account (Userbot) ကို ရယူခြင်း
    userbot = await get_assistant(chat_id)
    
    msg = await message.reply_text("🔄 **Starting Voice Chat...**")
    
    try:
        # Pyrogram ၏ invoke method ကိုသုံး၍ Group Call start ဖို့ ကြိုးစားခြင်း
        # (Userbot က Admin ဖြစ်မှသာ လုပ်ဆောင်နိုင်မည်)
        await userbot.invoke(
            functions.phone.CreateGroupCall(
                peer=await userbot.resolve_peer(chat_id),
                random_id=randint(10000, 99999)
            )
        )
        await msg.edit_text("✅ **Voice Chat has been started successfully!**")
        
    except Exception as e:
        # အကယ်၍ ဖွင့်ပြီးသားဖြစ်နေရင် သို့မဟုတ် Error တက်ရင်
        if "GROUPCALL_ALREADY_JOINED" in str(e) or "GROUPCALL_ALREADY_CREATED" in str(e):
            await msg.edit_text("⚠️ **Voice Chat is already active!**")
        elif "CHAT_ADMIN_REQUIRED" in str(e):
             await msg.edit_text("❌ **Assistant Account needs Admin rights to start VC.**\n\nAssistant Account ကို Admin ပေးထားရန် လိုအပ်ပါသည်။")
        else:
            await msg.edit_text(f"❌ **Failed to start VC:** `{e}`")


# --- (၂) VOICE CHAT ပိတ်ခြင်း (/closevc) ---
@app.on_message(filters.command(["closevc", "vcend", "endvc"]) & filters.group)
@AdminRightsCheck
async def stop_vc(client, message: Message, _, chat_id):
    # Assistant Account (Userbot) ကို ရယူခြင်း
    userbot = await get_assistant(chat_id)
    
    msg = await message.reply_text("🔄 **Closing Voice Chat...**")
    
    try:
        # Group Call ကို ရယူရန် ကြိုးစားခြင်း
        full_chat = await userbot.invoke(
            functions.channels.GetFullChannel(
                channel=await userbot.resolve_peer(chat_id)
            )
        )
        
        # Voice Chat မရှိရင်
        if not full_chat.full_chat.call:
             return await msg.edit_text("⚠️ **No active Voice Chat found to close.**")
             
        # Voice Chat ကို ဖျက်သိမ်းခြင်း (DiscardGroupCall)
        await userbot.invoke(
            functions.phone.DiscardGroupCall(
                call=full_chat.full_chat.call
            )
        )
        await msg.edit_text("✅ **Voice Chat has been closed successfully!**")
        
    except Exception as e:
        await msg.edit_text(f"❌ **Failed to close VC:** `{e}`")

# လိုအပ်သော Import များ
from pyrogram.raw import functions
from random import randint
