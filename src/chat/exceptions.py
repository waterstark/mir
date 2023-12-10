from uuid import UUID


class NoMatchError(Exception):
    """Raised when somebody tries to chat with a user with whom he/she has no match."""
    def __init__(self, user1_id: UUID, user2_id: UUID):
        super().__init__(f"No match for users {user1_id} and {user2_id}")
