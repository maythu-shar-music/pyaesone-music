autocoupledb = mongodb.auto_couple

async def add_auto_couple(chat_id: int):
    return await autocoupledb.update_one(
        {"chat_id": chat_id},
        {"$set": {"active": True}},
        upsert=True,
    )

async def remove_auto_couple(chat_id: int):
    return await autocoupledb.delete_one({"chat_id": chat_id})

async def get_auto_couples():
    chats = []
    async for doc in autocoupledb.find({"active": True}):
        chats.append(doc["chat_id"])
    return chats
