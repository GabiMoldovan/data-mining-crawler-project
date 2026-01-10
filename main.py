from menu.menu import Menu
from repository.transactionRepository import TransactionRepository
from repository.websiteRepository import WebsiteRepository
from service.crawlerService import CrawlerService
from service.miningService import MiningService
from service.scraperService import ScraperService
from service.websiteService import WebsiteService


import asyncio

async def main():
    websiteRepository = WebsiteRepository()
    transactionRepository = TransactionRepository()
    websiteService = WebsiteService(websiteRepository)
    scraperService = ScraperService()
    crawlerService = CrawlerService()
    miningService = MiningService(transactionRepository)

    menu = Menu(websiteService, scraperService, crawlerService, miningService)
    await menu.printMenu()

if __name__ == "__main__":
    asyncio.run(main())
