from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.base_config import current_user
from src.auth.models import User
from src.database import get_async_session
from src.posts.models import Post, Rating
from src.posts.schemas import CreatePost, EditPost, LikePost, ReadAllPosts

router = APIRouter(prefix="/posts", tags=["Post"])


@router.get("/", response_model=ReadAllPosts, status_code=status.HTTP_200_OK)
async def get_posts(session: AsyncSession = Depends(get_async_session)):
    query = select(Post).limit(10)
    result = await session.execute(query)
    posts = result.scalars().all()
    return {"data": posts}


@router.post("/", response_model=CreatePost, status_code=status.HTTP_201_CREATED)
async def upload_post(
    new_post: CreatePost,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    query = select(Post).where(Post.id == new_post.data.id)
    post = await session.execute(query)
    if post.scalar():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A post with such an ID already exists.",
        )
    stmt = insert(Post).values(**new_post.data.dict(), owner_id=user.id)
    await session.execute(stmt)
    await session.commit()
    return {"data": new_post.data}


@router.put("/{post_id}", response_model=EditPost, status_code=status.HTTP_200_OK)
async def edit_post(
    post_id: int,
    updated_post: EditPost,
    session: AsyncSession = Depends(get_async_session),
    verified_user: User = Depends(current_user),
):
    query = select(Post).where(Post.id == post_id)
    post = await session.execute(query)
    fetched_post = post.scalar()
    if fetched_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post was not found (id: {post_id})",
        )
    if fetched_post.owner_id != verified_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="unauthorized action",
        )
    stmt = update(Post).values(**updated_post.dict()).where(Post.id == post_id)
    await session.execute(stmt)
    await session.commit()
    return {"data": updated_post}


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def upload_post(
    post_id: int,
    session: AsyncSession = Depends(get_async_session),
    verified_user: User = Depends(current_user),
):
    query = select(Post).where(Post.id == post_id)
    post = await session.execute(query)
    fetched_post = post.scalar()
    if fetched_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post was not found (id: {post_id})",
        )
    if fetched_post.owner_id != verified_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="unauthorized action",
        )
    stmt = delete(Post).where(post_id == Post.id)
    await session.execute(stmt)
    await session.commit()


@router.post("/rating", status_code=status.HTTP_201_CREATED)
async def rate_post(
    rating_from_user: LikePost,
    session: AsyncSession = Depends(get_async_session),
    verified_user: User = Depends(current_user),
):
    query = select(Post).where(Post.id == rating_from_user.post_id)
    post = await session.execute(query)
    fetched_post = post.scalar()
    if fetched_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post was not found (id: {rating_from_user.post_id})",
        )
    if fetched_post.owner_id == verified_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="you can't rate your own post",
        )
    query = select(Rating).where(
        Rating.post_id == rating_from_user.post_id, Rating.user_id == verified_user.id,
    )
    vote = await session.execute(query)
    fetched_vote = vote.scalar()
    if fetched_vote is None and rating_from_user.like_is_toggeled:
        stmt = insert(Rating).values(
            **rating_from_user.dict(), user_id=verified_user.id,
        )
        await session.execute(stmt)
        stmt = (
            update(Post)
            .values(number_of_likes=fetched_post.number_of_likes + 1)
            .where(Post.id == fetched_post.id)
        )
        await session.execute(stmt)
    elif fetched_vote is None and not rating_from_user.like_is_toggeled:
        stmt = insert(Rating).values(
            **rating_from_user.dict(), user_id=verified_user.id,
        )
        await session.execute(stmt)
        stmt = (
            update(Post)
            .values(number_of_likes=fetched_post.number_of_likes - 1)
            .where(Post.id == fetched_post.id)
        )
        await session.execute(stmt)
    else:
        if rating_from_user.like_is_toggeled and fetched_vote.like_is_toggeled:
            stmt = (
                update(Post)
                .values(number_of_likes=fetched_post.number_of_likes - 1)
                .where(Post.id == rating_from_user.post_id)
            )
            await session.execute(stmt)
            stmt = delete(Rating).where(Rating.post_id == fetched_post.id)
            await session.execute(stmt)
        elif (
            not rating_from_user.like_is_toggeled and not fetched_vote.like_is_toggeled
        ):
            stmt = (
                update(Post)
                .values(number_of_likes=fetched_post.number_of_likes + 1)
                .where(Post.id == rating_from_user.post_id)
            )
            await session.execute(stmt)
            stmt = delete(Rating).where(Rating.post_id == fetched_post.id)
            await session.execute(stmt)
        elif rating_from_user.like_is_toggeled and not fetched_vote.like_is_toggeled:
            stmt = (
                update(Post)
                .values(number_of_likes=fetched_post.number_of_likes + 2)
                .where(Post.id == rating_from_user.post_id)
            )
            await session.execute(stmt)
            stmt = (
                update(Rating)
                .values(like_is_toggeled=rating_from_user.like_is_toggeled)
                .where(Rating.post_id == fetched_post.id)
            )
            await session.execute(stmt)
        elif not rating_from_user.like_is_toggeled and fetched_vote.like_is_toggeled:
            stmt = (
                update(Post)
                .values(number_of_likes=fetched_post.number_of_likes - 2)
                .where(Post.id == rating_from_user.post_id)
            )
            await session.execute(stmt)
            stmt = (
                update(Rating)
                .values(like_is_toggeled=rating_from_user.like_is_toggeled)
                .where(Rating.post_id == fetched_post.id)
            )
            await session.execute(stmt)
    await session.commit()
    return {"data": fetched_post}
