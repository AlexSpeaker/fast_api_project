from fastapi import FastAPI

from my_twitter.app.app import AppCreator
from my_twitter.app.database.database import DB
from my_twitter.settings import DATABASE_URL
import sentry_sdk

sentry_sdk.init(
    dsn="https://5b73bacfdc880b03c93b39bcda9ded9d@o4505970179964928.ingest.us.sentry.io/4507244038062080",
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
)

db: DB = DB(
    database_url=DATABASE_URL,
)

app: FastAPI = AppCreator(db).get_app
