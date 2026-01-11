from menu.menu import Menu
from repository.transactionRepository import TransactionRepository
from repository.websiteRepository import WebsiteRepository
from service.scraperService import ScraperService
from service.websiteService import WebsiteService
from service.miningService import MiningService


import asyncio

async def main():
    websiteRepository = WebsiteRepository()
    transactionRepository = TransactionRepository()
    websiteService = WebsiteService(websiteRepository)
    scraperService = ScraperService()
    miningService = MiningService(transactionRepository)

    menu = Menu(websiteService, scraperService, miningService)
    await menu.printMenu()

if __name__ == "__main__":
    asyncio.run(main())
