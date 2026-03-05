from abc import ABC, abstractmethod


class EmailServiceInterface(ABC):
    @abstractmethod
    async def send_verification_email(self, user_email: str, code: str) -> None: ...