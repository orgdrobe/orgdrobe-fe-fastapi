from sqlalchemy import Column, ForeignKey, Integer, String, TIMESTAMP, text

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
    picture = Column(String)

    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))


class Garment(Base):
    __tablename__ = "garments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
