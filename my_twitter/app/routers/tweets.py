from typing import Annotated, Any, Dict, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query, Request
from fastapi.params import Path
from sqlalchemy import and_, delete, select
from sqlalchemy.exc import IntegrityError

from my_twitter.app.database.database import DB
from my_twitter.app.database.models import ApiKey, Attachment, Like, Tweet
from my_twitter.app.routers.schemas.tweet import (
    TweetCreateOutSchema,
    TweetInSchema,
    TweetsOutSchema,
    TweetsResultOutSchema,
)
from my_twitter.app.utils.api_key import api_key_validator
from my_twitter.app.utils.dependencies import GetDBDIRInfo
from my_twitter.app.utils.file_manager import cleaner

router = APIRouter(
    tags=["tweets"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "/tweets",
    response_model=TweetCreateOutSchema,
    name="Create a tweet",
)
async def create_tweet(
    instance: Annotated[GetDBDIRInfo, Depends(GetDBDIRInfo)],
    data: Annotated[TweetInSchema, Body(...)],
    request: Request,
):
    """Роут для создания твита."""
    db: DB = instance.get_db()

    request_data: Dict[str, Any] = data.model_dump()
    async with db.get_session() as session:
        user = await api_key_validator(
            request.headers.get("api-key"), session, tweet=True
        )
        tweet = Tweet(
            content=request_data["tweet_data"],
        )
        attachments_q = await session.execute(
            select(Attachment).filter(
                Attachment.id.in_(request_data["tweet_media_ids"])
            )
        )
        attachments = attachments_q.scalars().all()
        tweet.attachments.extend(attachments)
        user.tweets.append(tweet)
        await session.commit()
    return tweet


@router.get(
    "/tweets",
    response_model=TweetsOutSchema,
    name="Get tweets",
)
async def get_tweets(
    instance: Annotated[GetDBDIRInfo, Depends(GetDBDIRInfo)],
    offset: Annotated[Optional[int], Query(..., gte=0)] = None,
    limit: Annotated[Optional[int], Query(..., gte=0)] = None,
):
    """Роут для получения всех твитов."""
    db: DB = instance.get_db()

    async with db.get_session() as session:
        sub_query = select(Tweet).order_by(Tweet.created.desc())
        if offset and limit:
            sub_query = sub_query.offset((offset - 1) * limit).limit(limit)
        tweets_q = await session.execute(sub_query)
        tweets = tweets_q.scalars().all()

        TweetsOutSchema.tweets = tweets

    return TweetsOutSchema


@router.delete(
    "/tweets/{tweet_id}",
    response_model=TweetsResultOutSchema,
    name="Delete tweet",
)
async def delete_tweet(
    instance: Annotated[GetDBDIRInfo, Depends(GetDBDIRInfo)],
    request: Request,
    tweet_id: Annotated[int, Path(..., gt=0)],
):
    """Роут удаления твита."""
    db: DB = instance.get_db()
    dir_info = instance.get_dir_info()
    async with db.get_session() as session:
        user = await api_key_validator(request.headers.get("api-key"), session)
        tweet_q = await session.execute(
            select(Tweet)
            .join(ApiKey, Tweet.user_id == ApiKey.user_id)
            .where(and_(Tweet.id == tweet_id, ApiKey.key == user.login.key))
        )
        tweet = tweet_q.scalars().one_or_none()
        if tweet is None:
            raise HTTPException(status_code=403, detail="Forbidden")
        files_path = [attachment.image_url for attachment in tweet.attachments]
        await session.execute(delete(Tweet).where(Tweet.id == tweet.id))
        await session.commit()
    TweetsResultOutSchema.result = True
    await cleaner(files_path, dir_info)
    return TweetsResultOutSchema


@router.post(
    "/tweets/{tweet_id}/likes",
    response_model=TweetsResultOutSchema,
    name="Like tweet",
)
async def like_tweet(
    instance: Annotated[GetDBDIRInfo, Depends(GetDBDIRInfo)],
    request: Request,
    tweet_id: Annotated[int, Path(..., gt=0)],
):
    """Роут для лайка твита."""
    db: DB = instance.get_db()
    async with db.get_session() as session:
        user = await api_key_validator(request.headers.get("api-key"), session)
        tweet_q = await session.execute(
            select(Tweet).where(
                and_(
                    Tweet.id == tweet_id,
                )
            )
        )
        tweet: Optional[Tweet] = tweet_q.scalars().one_or_none()
        if tweet is None:
            raise HTTPException(status_code=404, detail="Not Found")
        tweet.likes.append(Like(user=user))
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            TweetsResultOutSchema.result = False
            return TweetsResultOutSchema

    TweetsResultOutSchema.result = True
    return TweetsResultOutSchema


@router.delete(
    "/tweets/{tweet_id}/likes",
    response_model=TweetsResultOutSchema,
    name="Dislike tweet",
)
async def dislike_tweet(
    instance: Annotated[GetDBDIRInfo, Depends(GetDBDIRInfo)],
    request: Request,
    tweet_id: Annotated[int, Path(..., gt=0)],
):
    """Роут для удаления лайка с твита."""
    db: DB = instance.get_db()
    async with db.get_session() as session:
        user = await api_key_validator(request.headers.get("api-key"), session)
        like_q = await session.execute(
            select(Like).where(
                and_(
                    Like.user_id == user.id,
                    Like.tweet_id == tweet_id,
                )
            )
        )
        like = like_q.scalars().one_or_none()
        if not like:
            raise HTTPException(status_code=404, detail="Not Found")
        await session.execute(delete(Like).where(Like.id == like.id))
        await session.commit()

    TweetsResultOutSchema.result = True
    return TweetsResultOutSchema
