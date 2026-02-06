from pyrogram import filters, Client
from pyaesonemusic.utils.database import is_clone_bot 

@Client.on_message(filters.new_chat_members & filters.group)
async def auto_leave_logic(client, message):
    for member in message.new_chat_members:
        if member.is_bot:
            # အခုထည့်လိုက်တဲ့ function နဲ့ စစ်မယ်
            if await is_clone_bot(member.id):
                
                # ဝင်လာတဲ့ကောင်က ကိုယ်မဟုတ်ဘဲ တခြား clone ဖြစ်နေရင်...
                if member.id != client.me.id:
                    await message.reply_text(f"@{client.me.username} 𝓛𝓮𝓯𝓽 𝓣𝓱𝓮 𝓖𝓻𝓸𝓾𝓹😘.")
                    await client.leave_chat(message.chat.id)
