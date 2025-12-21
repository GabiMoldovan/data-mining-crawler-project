from menu.menu import Menu
from repository.websiteRepository import WebsiteRepository
from service.crawlerService import CrawlerService
from service.scraperService import ScraperService
from service.websiteService import WebsiteService


import asyncio

async def main():
    websiteRepository = WebsiteRepository()
    websiteService = WebsiteService(websiteRepository)
    scraperService = ScraperService()
    crawlerService = CrawlerService()

    menu = Menu(websiteService, scraperService, crawlerService)
    await menu.printMenu()

if __name__ == "__main__":
    asyncio.run(main())
