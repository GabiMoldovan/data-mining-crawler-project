from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from database import Base

class Material(Base):
    __tablename__ = "material"

    id = Column(Integer, primary_key=True, autoincrement=True)

    name = Column(String, nullable=False)
    certification = Column(String, nullable=True)
    is_certified = Column(Boolean, default=False)

    products = relationship(
        "ProductMaterial",
        back_populates="material",
        cascade="all, delete-orphan"
    )
