import os
from pathlib import Path

from my_twitter.settings import BASE_DIR, BASE_DIR_STATIC

TEST_BASE_DIR = os.path.abspath(os.path.dirname(__file__))

NAME_FOLDER_MEDIA: str = "images_test"
BASE_DIR_MEDIA: str = os.path.join(BASE_DIR_STATIC, NAME_FOLDER_MEDIA)
Path(BASE_DIR_MEDIA).mkdir(parents=True, exist_ok=True)
TEST_DIR_INFO = dict(
    BASE_DIR=BASE_DIR,
    BASE_DIR_STATIC=BASE_DIR_STATIC,
    NAME_FOLDER_MEDIA=NAME_FOLDER_MEDIA,
    BASE_DIR_MEDIA=BASE_DIR_MEDIA,
)
