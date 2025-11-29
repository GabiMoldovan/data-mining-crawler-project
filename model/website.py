from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database.database import Base

class Website(Base):
    __tablename__ = "website"

    id = Column(Integer, primary_key=True, autoincrement=True)
    website_name = Column(String, nullable=False)

    products = relationship(
        "Product",
        back_populates="website",
        lazy="select",
        cascade="all, delete-orphan"
    )
