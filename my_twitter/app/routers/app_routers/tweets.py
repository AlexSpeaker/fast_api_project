from typing import Annotated

from app.application.classes import CustomFastApi
from app.database.models import Attachment, Like, Tweet, User
from app.routers.app_routers.schemas.base import BaseSchema
from app.routers.app_routers.schemas.tweets import (
    InTweetSchema,
    OutBaseTweet,
    OutResponseTweet,
    OutSimpleResponseTweet,
    OutTweet,
)
from app.utils.utils import delete_img_file, get_user_or_test_user
from fastapi import APIRouter, Body, Header, Path, Query, Request, HTTPException
from sqlalchemy import exists, select

router = APIRouter(tags=["tweets"])


@router.post(
    "/tweets",
    response_model=OutSimpleResponseTweet,
    name="Создание нового твита.",
    description="Создание нового твита текущим пользователем (по умолчанию тестовый пользователь).",
)
async def create_tweet(
    data: Annotated[InTweetSchema, Body(...)],
    request: Request,
    api_key: Annotated[str, Header(...)] = "test",
) -> OutSimpleResponseTweet:
    """
    Создание нового твита.

    :param data: Данные, для создания твита.
    :param request: Request.
    :param api_key: API key пользователя.
    :return: OutSimpleResponseTweet.
    """

    app: CustomFastApi = request.app
    db = app.get_db()
    async with db.get_sessionmaker() as session:
        user = await get_user_or_test_user(session, app.get_settings(), api_key)

        attachments_q = await session.execute(
            select(Attachment).filter(Attachment.id.in_(data.tweet_media_ids))
        )
        attachments = attachments_q.scalars().all()

        tweet = Tweet(content=data.tweet_data, author=user)
        tweet.attachments.extend(attachments)
        session.add(tweet)
        await session.commit()
    return OutSimpleResponseTweet(tweet=OutBaseTweet.model_validate(tweet))


@router.get(
    "/tweets",
    response_model=OutResponseTweet,
    name="Получение всех твитов.",
    description="Получение всех твитов (с пагинацией).",
)
async def get_tweets(
    request: Request,
    offset: Annotated[int, Query(..., gte=0)] = 1,
    limit: Annotated[int, Query(..., gte=0)] = 10,
) -> OutResponseTweet:
    """
    Получение всех твитов (с пагинацией).

    :param offset: Страница.
    :param limit: Лимит на страницу.
    :param request: Request.
    :return: OutResponseTweet.
    """
    app: CustomFastApi = request.app
    db = app.get_db()
    settings = app.get_settings()
    async with db.get_sessionmaker() as session:
        tweets_q = await session.execute(
            select(Tweet)
            .order_by(Tweet.created.desc())
            .offset((offset - 1) * limit)
            .limit(limit)
        )
        tweets = tweets_q.scalars().all()
    validated_tweets = [
        OutTweet.model_validate(tweet).set_settings(settings) for tweet in tweets
    ]
    return OutResponseTweet(tweets=validated_tweets)


@router.delete(
    "/tweets/{tweet_id}",
    response_model=BaseSchema,
    name="Удаление твита по ID.",
    description="Удаление твита по ID при условии, что удаляет владелец твита.",
)
async def delete_tweet(
    request: Request,
    tweet_id: Annotated[int, Path(..., gt=0)],
    api_key: Annotated[str, Header(...)] = "test",
) -> BaseSchema:
    """
    Удаление твита по ID при условии, что удаляет владелец твита.

    :param request: Request.
    :param tweet_id: ID твита.
    :param api_key: API key пользователя.
    :return: BaseSchema.
    """
    app: CustomFastApi = request.app
    db = app.get_db()
    async with db.get_sessionmaker() as session:
        tweet_q = await session.execute(
            select(Tweet).join(User)
            .where(Tweet.id == tweet_id, User.api_key == api_key)
        )
        tweet = tweet_q.scalars().one_or_none()
        if not tweet:
            raise HTTPException(status_code=400, detail="Не верный запрос.")
        files_path = [att.image_path for att in tweet.attachments]
        await delete_img_file(*files_path, settings=app.get_settings())
        await session.delete(tweet)
        await session.commit()

    return BaseSchema()


@router.post(
    "/tweets/{tweet_id}/likes",
    response_model=BaseSchema,
    name="Лайк твита.",
    description="Текущий пользователь (по умолчанию тестовый пользователь) ставит лайк твиту.",
)
async def like_tweet(
    request: Request,
    tweet_id: Annotated[int, Path(..., gt=0)],
    api_key: Annotated[str, Header(...)] = "test",
) -> BaseSchema:
    """
    Текущий пользователь (по умолчанию тестовый пользователь) ставит лайк твиту.

    :param request: Request.
    :param tweet_id: ID твита.
    :param api_key: API key пользователя.
    :return: BaseSchema.
    """
    app: CustomFastApi = request.app
    db = app.get_db()
    async with db.get_sessionmaker() as session:
        user = await get_user_or_test_user(session, app.get_settings(), api_key)
        tweet_q = await session.execute(select(Tweet).where(Tweet.id == tweet_id))
        tweet = tweet_q.scalars().one()
        like_exists_q = await session.execute(
            select(
                exists().where(Like.user_id == user.id, Like.tweet_id == tweet_id)
            )
        )
        like_exists = like_exists_q.scalar()
        if like_exists:
            raise HTTPException(status_code=400, detail="Не верный запрос.")
        tweet.likes.append(Like(user=user))
        await session.commit()
    return BaseSchema()


@router.delete(
    "/tweets/{tweet_id}/likes",
    response_model=BaseSchema,
    name="Дизлайк твита.",
    description="Текущий пользователь (по умолчанию тестовый пользователь) убирает свой лайк у твита.",
)
async def dislike_tweet(
    request: Request,
    tweet_id: Annotated[int, Path(..., gt=0)],
    api_key: Annotated[str, Header(...)] = "test",
) -> BaseSchema:
    """
    Текущий пользователь (по умолчанию тестовый пользователь) убирает свой лайк у твита.

    :param request: Request.
    :param tweet_id: ID твита.
    :param api_key: API key пользователя.
    :return: BaseSchema.
    """
    app: CustomFastApi = request.app
    db = app.get_db()
    async with db.get_sessionmaker() as session:
        user = await get_user_or_test_user(session, app.get_settings(), api_key)
        tweet_q = await session.execute(select(Tweet).where(Tweet.id == tweet_id))
        tweet = tweet_q.scalars().one()
        like_q = await session.execute(
            select(Like).where(Like.user_id == user.id, Like.tweet_id == tweet_id)
        )
        like = like_q.scalars().one_or_none()
        if not like:
            raise HTTPException(status_code=400, detail="Не верный запрос.")
        tweet.likes.remove(like)
        await session.commit()
    return BaseSchema()
