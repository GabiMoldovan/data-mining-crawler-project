from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base

class Product(Base):
    __tablename__ = "product" # Many to one with website

    id = Column(Integer, primary_key=True, autoincrement=True) # PK, Strategy: autoincrement
    product_name = Column(String, nullable=False)
    price = Column(Float, nullable=False)

    website_id = Column(Integer, ForeignKey("website.id"))
    website = relationship("Website", back_populates="products")
