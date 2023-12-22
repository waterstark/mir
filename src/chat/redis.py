import json
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import AuthUser
from src.chat.schemas import WSMessageRequest
from src.matches.crud import get_match_by_user_ids
from src.matches.models import Match
from src.redis.redis import redis as redis_client


async def get_message_pk() -> uuid.UUID:
    """
    Return primary key for message.
    Can be got from redis or from python.
    Need cause we do not save messages to db when it is sent.
    """
    # TODO: replace with normal pk pick
    return uuid.uuid4()


async def get_match(
    session: AsyncSession,
    user: AuthUser,
    ws_msg: WSMessageRequest,
) -> Match:
    """
    Getting a Match from the cache and adding it to the cache if it is not there.
    """
    match = await redis_client.get(f"match_{ws_msg.message.match_id}")
    if match is not None:
        match = json.loads(match)
    else:
        match = await get_match_by_user_ids(session, user.id, ws_msg.message.to_id)
        if match is None:
            return match
        dict_match = {
            "match_id": str(match.id),
            "user1_id": str(match.user1_id),
            "user2_id": str(match.user2_id),
            "created_at": str(match.created_at),
        }
        await redis_client.set(f"match_{ws_msg.message.match_id}", json.dumps(dict_match))

    return match
