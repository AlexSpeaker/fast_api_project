from pydantic import Field, computed_field

from my_twitter.app.routers.schemas.user import UserBase


class UserLikeOutShort(UserBase):
    id: int = Field(exclude=True)

    @computed_field
    def name(self) -> str:
        return f"{self.first_name} {self.surname}"

    @computed_field
    def user_id(self) -> int:
        return self.id

    class ConfigDict:
        from_attributes = True
