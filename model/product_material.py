from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class ProductMaterial(Base):
    __tablename__ = "product_material"

    id = Column(Integer, primary_key=True, autoincrement=True)

    product_id = Column(Integer, ForeignKey("product.id"), nullable=False)
    material_id = Column(Integer, ForeignKey("material.id"), nullable=False)

    percentage = Column(Integer, nullable=False)
    area = Column(String, nullable=True)

    product = relationship("Product", back_populates="materials")
    material = relationship("Material", back_populates="products")
