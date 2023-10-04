import uuid


async def get_message_pk() -> uuid.UUID:
    """
    Return primary key for message.
    Can be got from redis or from python.
    Need cause we do not save messages to db when it is sent.
    """
    # TODO: replace with normal pk pick
    return uuid.uuid4()
