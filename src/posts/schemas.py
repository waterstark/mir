
from pydantic import BaseModel, StrictStr


class Post(BaseModel):
    id: int
    title: StrictStr

    class Config:
        orm_mode = True


class ReadAllPosts(BaseModel):
    data: list[Post]

    class Config:
        orm_mode = True


class CreatePost(BaseModel):
    data: Post

    class Config:
        orm_mode = True


class EditPost(BaseModel):
    title: StrictStr | None | None

    class Config:
        orm_mode = True


class LikePost(BaseModel):
    post_id: int
    like_is_toggeled: bool | None

    class Config:
        orm_mode = True
