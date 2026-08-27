from pydantic import ConfigDict

from schemas.base_model import CamelCaseBaseModel


class NewGarmentType(CamelCaseBaseModel):
    name: str
    description: str


class UpdateGarmentType(CamelCaseBaseModel):
    name: str | None = None
    description: str | None = None


class GarmentTypeOut(CamelCaseBaseModel):
    id: int
    name: str
    description: str

    model_config = ConfigDict(from_attributes=True)

