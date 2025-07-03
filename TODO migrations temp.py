from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    user_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    username = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255), index=True)
    registration_date = Column(DateTime, nullable=False, default=func.now(), index=True)

class Gender(Base):
    __tablename__ = 'gender'

    gender_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)

class Profile(Base):
    __tablename__ = 'profile'

    profile_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, ForeignKey('user.user_id'), nullable=False, index=True)
    user = relationship("User")
    birthdate = Column(Date, index=True)
    contact = Column(String(255), index=True)
    address = Column(String(255), index=True)
    gender_id = Column(Integer, ForeignKey('gender.gender_id'), index=True)
    gender = relationship("Gender")
    biography = Column(Text, index=True)
    avatar = Column(String(255), index=True)
