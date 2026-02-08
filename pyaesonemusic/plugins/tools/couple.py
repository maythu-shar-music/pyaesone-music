import os
import random
import asyncio
import time
from datetime import datetime
from PIL import Image, ImageDraw
from pyrogram import filters

from maythusharmusic import app
from assets.couple import _get_couple, _save_couple, add_auto_couple, remove_auto_couple, get_auto_couples
from maythusharmusic.utils.decorators import AdminRightsCheck

# --- CONFIGURATION (ယခင်အတိုင်း) ---
BG_IMAGE_PATH = "assets/couple.jpg" 
DOWNLOAD_DIR = "downloads"
P1_COORDS = (180, 190) 
P2_COORDS = (860, 190) 
PROFILE_SIZE = (380, 380)
# ---------------------

# --- Helper Function: ပုံဖန်တီးခြင်း ---
def make_colage(p1_path, p2_path, chat_id):
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)
        
    output_path = f"{DOWNLOAD_DIR}/couple_{chat_id}.png"
    
    if os.path.exists(BG_IMAGE_PATH):
        bg = Image.open(BG_IMAGE_PATH)
    else:
        bg = Image.new("RGB", (1280, 720), "white")

    img1 = Image.open(p1_path).resize(PROFILE_SIZE)
    img2 = Image.open(p2_path).resize(PROFILE_SIZE)

    mask = Image.new("L", PROFILE_SIZE, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + PROFILE_SIZE, fill=255)

    img1.putalpha(mask)
    img2.putalpha(mask)

    bg.paste(img1, P1_COORDS, img1)
    bg.paste(img2, P2_COORDS, img2)

    bg.save(output_path)
    return output_path

# --- Helper Function: Couple ရွေးချယ်ပြီး ပို့ခြင်း ---
async def generate_and_send_couple(chat_id, message=None):
    try:
        today = int(time.time())
        list_of_users = []

        # Member များရှာခြင်း
        async for member in app.get_chat_members(chat_id, limit=200):
            if not member.user.is_bot and not member.user.is_deleted:
                if member.user.photo:
                    list_of_users.append(member.user.id)

        if len(list_of_users) < 2:
            if message:
                await message.reply_text("⚠️ Not enough members with profile photos!")
            return

        c1_id = random.choice(list_of_users)
        c2_id = random.choice(list_of_users)
        while c1_id == c2_id:
            c2_id = random.choice(list_of_users)

        p1_file = f"{DOWNLOAD_DIR}/p1_{c1_id}.jpg"
        p2_file = f"{DOWNLOAD_DIR}/p2_{c2_id}.jpg"

        user1 = await app.get_chat(c1_id)
        user2 = await app.get_chat(c2_id)
        
        await app.download_media(user1.photo.big_file_id, file_name=p1_file)
        await app.download_media(user2.photo.big_file_id, file_name=p2_file)

        couple_img = make_colage(p1_file, p2_file, chat_id)

        await _save_couple(chat_id, c1_id, c2_id, today)

        caption = f"""
**Couple of the Moment! ❤️**

{user1.first_name} + {user2.first_name} = 💘

━━━━━━━━━━━━━━━━━━━━
**New couple selected automatically.**
"""
        await app.send_photo(chat_id, photo=couple_img, caption=caption)

        if os.path.exists(p1_file): os.remove(p1_file)
        if os.path.exists(p2_file): os.remove(p2_file)
        if os.path.exists(couple_img): os.remove(couple_img)

    except Exception as e:
        if message:
            await message.reply_text(f"Error: {e}")
        print(f"Auto Couple Error in {chat_id}: {e}")


# --- Command: Manual Couple Selection ---
@app.on_message(filters.command(["couple", "couples"]) & filters.group)
async def couple_handler(client, message):
    chat_id = message.chat.id
    today = int(time.time())
    THREE_HOURS = 10800 

    is_couple = await _get_couple(chat_id)

    # ၃ နာရီမပြည့်သေးရင် အဟောင်းပြမယ်
    if is_couple:
        saved_time = is_couple.get("time", 0)
        if (today - saved_time) < THREE_HOURS:
            u1_id = is_couple["u1"]
            u2_id = is_couple["u2"]
            try:
                c1 = (await app.get_users(u1_id)).first_name
                c2 = (await app.get_users(u2_id)).first_name
            except:
                c1, c2 = "Unknown", "Unknown"

            remaining = THREE_HOURS - (today - saved_time)
            hours, mins = int(remaining / 3600), int((remaining % 3600) / 60)
            
            return await message.reply_text(f"❣️ **Active Couple:** {c1} + {c2}\n⏳ Next change in: {hours}h {mins}m")

    # ၃ နာရီကျော်ရင် အသစ်ထုတ်မယ်
    msg = await message.reply_text("📸 **Generating...**")
    await generate_and_send_couple(chat_id, message)
    await msg.delete()


# --- Command: Enable/Disable Auto Mode ---
@app.on_message(filters.command("autocouple") & filters.group)
@AdminRightsCheck
async def auto_couple_switch(client, message):
    if len(message.command) != 2:
        return await message.reply_text("Usage: `/autocouple [on|off]`")
    
    state = message.command[1].lower()
    if state == "on":
        await add_auto_couple(message.chat.id)
        await message.reply_text("✅ **Auto Couple Mode Activated!**\nI will send a new couple every 3 hours.")
    elif state == "off":
        await remove_auto_couple(message.chat.id)
        await message.reply_text("❌ **Auto Couple Mode Disabled.**")
    else:
        await message.reply_text("Usage: `/autocouple [on|off]`")


# --- BACKGROUND TASK: 3 Hour Loop ---
async def auto_couple_background_task():
    while True:
        # ၃ နာရီ (၁၀၈၀၀ စက္ကန့်) စောင့်မည်
        await asyncio.sleep(10800)
        
        # Auto ဖွင့်ထားသော Group များကို ယူမည်
        active_chats = await get_auto_couples()
        
        for chat_id in active_chats:
            try:
                # Couple ထုတ်ပြီး ပို့မည်
                await generate_and_send_couple(chat_id)
                # FloodWait ရှောင်ရန် ၅ စက္ကန့်ခြားမည်
                await asyncio.sleep(5)
            except Exception as e:
                print(f"Failed to auto send couple to {chat_id}: {e}")

# Task ကို Start လုပ်ခြင်း
asyncio.create_task(auto_couple_background_task())
