from database import Database
from model.product import Product
from model.website import Website
from repository.websiteRepository import WebsiteRepository
from service.crawlerService import CrawlerService
from service.scraperService import ScraperService
import asyncio

from service.websiteService import WebsiteService


async def main():
    print("Goodbye, world!")

    try:
        websiteRepository = WebsiteRepository()
        websiteService = WebsiteService(websiteRepository)

        websiteService.deleteEverythingFromDatabase()
        site = Website(website_name="Test Shop")
        websiteService.createWebsite(site)
    except Exception as ex:
        print(ex)


    scraper = ScraperService()

    test_url = "https://www.bershka.com/ro/hanorac-oversize-fermoar-glug%C4%83-c0p193051059.html?colorId=717"

    result = await scraper.scrapeURL(test_url)

    result = scraper.createProduct(result, 1)

    print(result.toString())

    '''
    try:
        crawler = CrawlerService()
        test_url = "https://www.bershka.com/ro/"

        results = crawler.crawl_website(test_url, max_pages=20, output_files=True)

        crawler.close()
        if results:
            print("\nResults returned successfully!")
            print(f"Total filtered URLs: {results['categorization']['total']}")
            print(f"Product URLs: {results['categorization']['product_count']}")
            print(f"Category URLs: {results['categorization']['category_count']}")

        return results

    except Exception as e:
        print(f"Error in main: {e}")
        return None
    '''


if __name__ == "__main__":
    asyncio.run(main())
