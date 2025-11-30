from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database.database import Base

class Website(Base):
    __tablename__ = "website" # One to many with products

    id = Column(Integer, primary_key=True, autoincrement=True) # PK, Strategy: autoincrement
    website_name = Column(String, nullable=False, unique=True) # Website name is unique

    products = relationship(
        "Product",
        back_populates="website",
        lazy="select",
        cascade="all, delete-orphan"
    )
