from sqlalchemy import Integer

from database import Database
from model import Website, Product


class WebsiteRepository:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(WebsiteRepository, cls).__new__(cls)
        return cls._instance


    def __init__(self):
        if hasattr(self, "_initialized") and self._initialized:
            return

        self.__db = Database()
        self._initialized = True


    def getWebsiteById(self, websiteId: Integer)->Website|None:
        with self.__db.session() as session:
            return session.query(Website).filter(Website.id == websiteId).first()


    def getWebsiteByName(self, websiteName: str)->Website|None:
        with self.__db.session() as session:
            return session.query(Website).filter(Website.website_name == websiteName).first()


    def createWebsite(self, website: Website)->None:
        with self.__db.session() as session:
            session.add(website)


    def addProduct(self, product: Product)->None:
        with self.__db.session() as session:
            session.add(product)
