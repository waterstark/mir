import uuid

from motor.motor_asyncio import AsyncIOMotorClient

from src.config import settings


class Mongo:
    def __init__(self):
        self.client_mongo = AsyncIOMotorClient(settings.db_url_mongo)
        self.mongo_client = self.client_mongo.database
        self.collection = self.mongo_client.message

    async def create_message(self, message: dict):
        await self.collection.insert_one(message)
        return {"message": "message successfully added"}

    async def get_message(self, match_id: uuid):
        return await self.collection.find({"chat_id": {"$eq": match_id}})

    async def update_message(self, id_message: uuid):
        return await self.collection.update_one(
            {"id_message": id_message},
            {"$set": {"key": "value"}},
        )

    async def delete_message(self, id_message: uuid):
        await self.collection.delete_one({"id_message": id_message})
        return {"message": "message successfully deleted"}


mongo = Mongo()
