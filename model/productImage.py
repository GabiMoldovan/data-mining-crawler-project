from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base


class ProductImage(Base):
    __tablename__ = "product_image"

    id = Column(Integer, primary_key=True, autoincrement=True)
    image_url = Column(String, nullable=False)

    product_id = Column(Integer, ForeignKey("product.id"))
    product = relationship("Product", back_populates="images")
