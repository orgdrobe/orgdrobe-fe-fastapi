from .generic_repo_interface import GenericRepositoryInterface
from models import Color


class ColorRepositoryInterface(GenericRepositoryInterface[Color]):
    ...

