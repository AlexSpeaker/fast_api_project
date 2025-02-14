from pydantic import BaseModel


class BaseSchema(BaseModel):
    """
    Класс-схема. Базовая модель.
    """

    result: bool = True
