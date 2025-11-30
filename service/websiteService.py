from sqlalchemy import Integer

from model import Website, Product


class WebsiteService:
    def __init__(self,
                 websiteRepository,
                 ):
        self.__websiteRepository = websiteRepository

    def getWebsiteById(self, websiteId: Integer) -> Website|None:
        return self.__websiteRepository.getWebsiteById(websiteId)

    def getWebsiteByName(self, websiteName: str) -> Website|None:
        return self.__websiteRepository.getWebsiteByName(websiteName)

    def createWebsite(self, website: Website) -> None:
        self.__websiteRepository.createWebsite(website)

    def addProduct(self, product: Product) -> None:
        self.__websiteRepository.addProduct(product)
