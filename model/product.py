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

    def toString(self) -> str:
        if self.colors:
            colors_str = "\n".join([f"    - {c.color_id} ({c.name})" for c in self.colors])
        else:
            colors_str = "    None"

        if self.origins:
            origins_str = "\n".join([f"    - {o.name}" for o in self.origins])
        else:
            origins_str = "    None"

        if self.images:
            images_str = "\n".join([f"    - {img.image_url}" for img in self.images])
        else:
            images_str = "    None"

        if hasattr(self, "website") and self.website:
            website_str = f"{self.website_id} ({self.website.website_name})"
        else:
            website_str = str(self.website_id)

        return (
            f"Product:\n"
            f"  id: {self.id}\n"
            f"  name: {self.product_name}\n"
            f"  description: {self.product_description}\n"
            f"  url: {self.product_url}\n"
            f"  main_image: {self.product_main_image}\n"
            f"  price: {self.product_price}\n"
            f"  sku: {self.product_sku}\n"
            f"  reference: {self.product_reference}\n"
            f"  display_reference: {self.product_display_reference}\n"
            f"  in_stock: {self.product_in_stock}\n"
            f"  reference_text: {self.product_reference_text}\n"
            f"  model_height: {self.product_model_height}\n"
            f"  model_size: {self.product_model_size}\n"
            f"  model_name: {self.product_model_name}\n"
            f"  extra_info: {self.product_extra_info}\n"
            f"  website: {website_str}\n"
            f"  colors:\n{colors_str}\n"
            f"  origins:\n{origins_str}\n"
            f"  images:\n{images_str}"
        )

