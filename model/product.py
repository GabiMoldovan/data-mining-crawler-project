from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base

class Product(Base):
    __tablename__ = "product"

    id = Column(Integer, primary_key=True, autoincrement=True) # PK, Strategy: autoincrement
    product_name = Column(String, nullable=False)
    product_description = Column(String)
    product_url = Column(String)
    product_main_image = Column(String)
    product_price = Column(Float, nullable=False)
    product_sku = Column(String)
    product_reference = Column(String)
    product_display_reference = Column(String)
    product_in_stock = Column(String)
    product_reference_text = Column(String)
    product_model_height = Column(String)
    product_model_size = Column(String)
    product_model_name = Column(String)
    product_extra_info = Column(String)

    # many-to-one
    website_id = Column(Integer, ForeignKey("website.id"))
    website = relationship("Website", back_populates="products")

    # many-to-many Colors
    colors = relationship(
        "Color",
        secondary="products_colors",
        back_populates="products"
    )

    # one-to-many Images
    images = relationship(
        "ProductImage",
        back_populates="product",
        cascade="all, delete-orphan"
    )

    # many-to-many Origins
    origins = relationship(
        "Origin",
        secondary="products_origins",
        back_populates="products"
    )