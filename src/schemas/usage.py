from pydantic import ConfigDict

from schemas.base_model import CamelCaseBaseModel


class NewUsage(CamelCaseBaseModel):
    name: str
    description: str


class UpdateUsage(CamelCaseBaseModel):
    name: str | None = None
    description: str | None = None


class UsageOut(CamelCaseBaseModel):
    id: int
    name: str
    description: str

    model_config = ConfigDict(from_attributes=True)

