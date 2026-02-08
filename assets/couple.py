import random
from datetime import datetime
import string
import time
from typing import Dict, List, Union, Any
from pyaesonemusic.core.mongo import mongodb, pymongodb

coupledb = {}
# in memory storage

# ရှိပြီးသား coupledb အောက်မှာ ထည့်ပါ
autocoupledb = mongodb.auto_couple

# Auto ဖွင့်ထားသော Group များကို စာရင်းသွင်းခြင်း
async def add_auto_couple(chat_id: int):
    return await autocoupledb.update_one(
        {"chat_id": chat_id},
        {"$set": {"active": True}},
        upsert=True,
    )

# Auto ပိတ်ခြင်း
async def remove_auto_couple(chat_id: int):
    return await autocoupledb.delete_one({"chat_id": chat_id})

# Auto ဖွင့်ထားသော Group အားလုံးကို ယူခြင်း
async def get_auto_couples():
    chats = []
    async for doc in autocoupledb.find({"active": True}):
        chats.append(doc["chat_id"])
    return chats

async def _get_lovers(cid: int):
    chat_data = coupledb.get(cid, {})
    lovers = chat_data.get("couple", {})
    return lovers


async def get_image(cid: int):
    chat_data = coupledb.get(cid, {})
    image = chat_data.get("img", "")
    return image


async def get_couple(cid: int, date: str):
    lovers = await _get_lovers(cid)
    return lovers.get(date, False)


async def save_couple(cid: int, date: str, couple: dict, img: str):
    if cid not in coupledb:
        coupledb[cid] = {"couple": {}, "img": ""}
    coupledb[cid]["couple"][date] = couple
    coupledb[cid]["img"] = img
