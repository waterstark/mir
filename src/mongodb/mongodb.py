import uuid

from src.database import client_mongo

db = client_mongo.database
collection = db.message


async def create_message(message: dict):
    await collection.insert_one(message)
    return {"message": "message successfully added"}


async def get_message(match_id: uuid):
    return await collection.find({"chat_id": {"$eq": match_id}})


async def update_message(id_message: uuid):
    return await collection.update_one(
        {"id_message": id_message}, {"$set": {"key": "value"}},
    )


async def delete_message(id_message: uuid):
    await collection.delete_one({"id_message": id_message})
    return {"message": "message successfully deleted"}
