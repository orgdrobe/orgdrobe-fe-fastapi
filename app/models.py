from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import Column, ForeignKey, Integer, String, TIMESTAMP, text, CheckConstraint
from sqlalchemy.orm import Mapped

from .database import Base

# SQLAlchemy Models (Database Tables)

# TODO add validation like in Pydantic Models (schemas.py) (a nullable field with minimum length: `name: str | None = Field(default=None,  min_length=1)`)??? nah, too much code

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    login = Column(String, index=True, unique=True, nullable=False)
    email = Column(String, index=True, unique=True, nullable=False)
    password = Column(String, nullable=False)
    
    name = Column(String)
    image_link: Column[str] = Column(String)
    image_id: Column[int] = Column(Integer, ForeignKey("images_info.id"))

    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'), onupdate=lambda: datetime.now(timezone.utc))


class Garment(Base):
    __tablename__ = "garments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    image_link: Column[str] = Column(String)
    
    last_worn: Mapped[Optional[datetime]]
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    image_id = Column(Integer, ForeignKey("images_info.id"))
    
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'), onupdate=lambda: datetime.now(timezone.utc))

class Outfit(Base):
    __tablename__ = "outfits"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    image_link: Column[str] = Column(String)
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    image_id: Column[int] = Column(Integer, ForeignKey("images_info.id"))
    
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'), onupdate=lambda: datetime.now(timezone.utc))

class OutfitGarment(Base):
    __tablename__ = "outfit_garments"
    
    outfit_id = Column(Integer, ForeignKey('outfits.id'), primary_key=True, nullable=False)
    garment_id = Column(Integer, ForeignKey('garments.id'), primary_key=True, nullable=False)

    order = Column(Integer, default=0)
    notes = Column(String)

    added_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

class ImageInfo(Base):
    __tablename__ = "images_info"
    
    id = Column(Integer, primary_key=True, index=True)

    filename_store = Column(String, nullable=False)
    filename_original = Column(String)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'), onupdate=lambda: datetime.now(timezone.utc))


class Gender(Base):
    __tablename__ = "genders"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'), onupdate=lambda: datetime.now(timezone.utc))

class CategoryMaster(Base):
    __tablename__ = "categories_master"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'), onupdate=lambda: datetime.now(timezone.utc))

class CategorySub(Base):
    __tablename__ = "categories_sub"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'), onupdate=lambda: datetime.now(timezone.utc))

class Type(Base):
    __tablename__ = "types"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'), onupdate=lambda: datetime.now(timezone.utc))

class Color(Base): # because of dataset
    __tablename__ = "colors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    hex = Column(String(7))
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'), onupdate=lambda: datetime.now(timezone.utc))
    __table_args__ = (
        CheckConstraint("hex ~ '^#[0-9A-Fa-f]{6}$'", name="hex_regex"),
    )

class Season(Base):
    __tablename__ = "seasons"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'), onupdate=lambda: datetime.now(timezone.utc))

class Usage(Base):
    __tablename__ = "usages"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'), onupdate=lambda: datetime.now(timezone.utc))

