from typing import List

from pydantic import BaseModel, Field, computed_field


class UserBase(BaseModel):
    first_name: str = Field(exclude=True)
    middle_name: str = Field(exclude=True)
    surname: str = Field(exclude=True)


class UserOutShort(UserBase):
    id: int

    @computed_field
    def name(self) -> str:
        return f"{self.first_name} {self.surname}"

    class ConfigDict:
        from_attributes = True


class UserOutFollowersFollowing(UserOutShort):

    users_in_my_subscriptions: List[UserOutShort] = Field(exclude=True)
    users_following_me: List[UserOutShort] = Field(exclude=True)

    @computed_field
    def following(self) -> List[UserOutShort]:
        return self.users_in_my_subscriptions

    @computed_field
    def followers(self) -> List[UserOutShort]:
        return self.users_following_me

    class ConfigDict:
        from_attributes = True


class UserOutSuccessfully(BaseModel):
    result: bool = True
    user: UserOutFollowersFollowing

    class ConfigDict:
        from_attributes = True


class UserResultOutSchema(BaseModel):
    result: bool
