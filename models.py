from database import Base
from sqlalchemy import Integer, String, Date, Column, ForeignKey, Boolean
from sqlalchemy.orm import relationship

class Contact(Base):
    __tablename__ = 'contacts'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(50), unique=True, nullable=False)
    phone = Column (String(100), nullable=False)
    birthday = Column (Date, nullable=False)
    additional_info = Column(String(500), nullable=True)

    user = relationship('User', back_populates='contacts')


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String(250), unique=True, nullable=False)
    hashed_password = Column(String(500), nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    avatar_url = Column(String(500), nullable=True)

    contacts = relationship('Contact', back_populates='user')





