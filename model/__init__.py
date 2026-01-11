from sqlalchemy import ForeignKey, Integer, Column, Table

from database import Base
from .product import Product
from .website import Website
from .color import Color
from .origin import Origin
from .productImage import ProductImage
from .crawledUrl import CrawledUrl
from .material import Material
from .product_material import ProductMaterial

product_colors_table = Table(
    "products_colors",
    Base.metadata,
    Column("product_id", Integer, ForeignKey("product.id"), primary_key=True),
    Column("color_id", Integer, ForeignKey("color.id"), primary_key=True),
)

product_origins_table = Table(
    "products_origins",
    Base.metadata,
    Column("product_id", Integer, ForeignKey("product.id"), primary_key=True),
    Column("origin_id", Integer, ForeignKey("origin.id"), primary_key=True),
)
