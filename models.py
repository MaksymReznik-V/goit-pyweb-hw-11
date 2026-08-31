from database import Base
from sqlalchemy import Integer, String, Date, Column

class Contact(Base):
    __tablename__ = 'contacts'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(50), unique=True, nullable=False)
    phone = Column (String(100), nullable=False)
    birthday = Column (Date, nullable=False)
    additional_info = Column(String(500), nullable=True)
