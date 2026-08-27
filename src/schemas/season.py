from pydantic import ConfigDict

from schemas.base_model import CamelCaseBaseModel


class NewSeason(CamelCaseBaseModel):
    name: str
    description: str


class UpdateSeason(CamelCaseBaseModel):
    name: str | None = None
    description: str | None = None


class SeasonOut(CamelCaseBaseModel):
    id: int
    name: str
    description: str

    model_config = ConfigDict(from_attributes=True)

