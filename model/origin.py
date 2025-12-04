from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database.database import Base

class Origin(Base):
    __tablename__ = "origin"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

    products = relationship(
        "Product",
        secondary="products_origins",
        back_populates="origins"
    )