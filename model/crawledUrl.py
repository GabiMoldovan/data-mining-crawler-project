from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base

class CrawledUrl(Base):
    __tablename__ = "crawled_url" # One to many with products

    id = Column(Integer, primary_key=True, autoincrement=True) # PK, Strategy: autoincrement
    crawled_url_address = Column(String, nullable=False, unique=True) # Crawled URL should be unique name is unique

    # many-to-one
    website_id = Column(Integer, ForeignKey("website.id"))
    website = relationship("Website", back_populates="crawled_urls")
