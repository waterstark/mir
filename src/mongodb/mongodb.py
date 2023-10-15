import datetime
import uuid

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.results import DeleteResult, UpdateResult

from src.chat.schemas import MessageCreateRequest, MessageResponse
from src.chat.util import MessageStatus
from src.config import settings


class Mongo:
    def __init__(self):
        self.client_mongo = AsyncIOMotorClient(
            settings.db_url_mongo,
            serverSelectionTimeoutMS=5000,
            uuidRepresentation="pythonLegacy",
        )
        self.mongo_client = self.client_mongo.database
        self.collection = self.mongo_client.message

    async def create_message(self, message: MessageCreateRequest) -> MessageResponse:
        # TODO: find out if we can force _id=uuid for all documents
        dt = datetime.datetime.utcnow()
        result = await self.collection.insert_one({
            **message.dict(),
            "_id": uuid.uuid4(),
            "updated_at": dt,
            "status": MessageStatus.SENT,
        })

        return MessageResponse(
            **dict(message),
            id=result.inserted_id,
            status=MessageStatus.SENT,
            updated_at=dt,
        )

    async def get_message(self, message_id: uuid.UUID) -> dict | None:
        return await self.collection.find_one(filter=message_id)

    async def update_message(self, message: MessageResponse) -> UpdateResult:
        return await self.collection.update_one(
            {"_id": message.id},
            {"$set": {**message.dict(exclude={"id"})}},
        )

    async def delete_message(self, message_id: uuid) -> DeleteResult:
        return await self.collection.delete_one({"_id": message_id})
