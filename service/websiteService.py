class WebsiteService:
    def __init__(self,
                 websiteRepository,
                 ):
        self.__websiteRepository = websiteRepository

    def getWebsiteById(self, websiteId):
        return self.__websiteRepository.getWebsiteById(websiteId)

    def createWebsite(self, website):
        self.__websiteRepository.createWebsite(website)

    def addProduct(self, product):
        self.__websiteRepository.addProduct(product)