from pydantic import BaseModel, Field, computed_field


class MediaCreateOutSchema(BaseModel):
    id: int = Field(exclude=True)
    result: bool = True

    @computed_field
    def media_id(self) -> int:
        return self.id

    class ConfigDict:
        from_attributes = True
