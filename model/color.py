from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database.database import Base

class Color(Base):
    __tablename__ = "color"

    id = Column(Integer, primary_key=True, autoincrement=True)
    color_id = Column(String)
    name = Column(String)

    products = relationship(
        "Product",
        secondary="products_colors",
        back_populates="colors"
    )