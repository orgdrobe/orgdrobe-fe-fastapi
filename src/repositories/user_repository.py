from typing import Optional

from sqlalchemy.orm import Session

from models.user import User

class UserRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add_user(self, user: User) -> User:
        self._session.add(user)
        self._session.flush()
        self._session.refresh(user)
        return user