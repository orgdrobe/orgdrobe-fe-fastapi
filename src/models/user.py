from datetime import datetime

from sqlalchemy import String, DateTime, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import ModelBase

class User(ModelBase):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text('now()'), onupdate=text('now()'))


