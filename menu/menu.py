import asyncio

from model import Website, CrawledUrl
from service.crawlerService import CrawlerService
from service.scraperService import ScraperService
from service.websiteService import WebsiteService

class Menu:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Menu, cls).__new__(cls)
        return cls._instance

    def __init__(self, websiteService: WebsiteService, scraperService: ScraperService, crawlerService: CrawlerService):
        if hasattr(self, "_initialized") and self._initialized:
            return

        self.__websiteService = websiteService
        self.__scraperService = scraperService
        self.__crawlerService = crawlerService
        self._initialized = True

    async def printMenu(self):
        while True:
            print(
                "1. Ruleaza crawler pe Bershka si extrage produsele (!!! SE STERG PRODUSELE EXTRASE ANTERIOR DIN BAZA DE DATE !!!)")
            print("2. Scrape URL")
            print("3. Tehnica de data mining 1")
            print("4. Tehnica de data mining 2")
            print("5. Exit\n")

            option = int(await asyncio.to_thread(input, "Alegeti optiunea: "))
            print()

            if option == 1:
                try:
                    # Delete every entry into the database
                    self.__websiteService.deleteEverythingFromDatabase()

                    websiteUrl = "https://www.bershka.com/ro/"
                    website = Website(website_name=websiteUrl)

                    # Create website
                    self.__websiteService.createWebsite(website)
                    website_id = self.__websiteService.getWebsiteByName(websiteUrl).id

                    # Number of pages that you want to crawl. Maybe make it to be given as input?
                    max_pages = 50

                    # Crawl website
                    results = await asyncio.to_thread(
                        self.__crawlerService.crawl_website,
                        websiteUrl,
                        max_pages,
                        True
                    )
                    self.__crawlerService.close()

                    # Read every crawled url for products
                    lines = await asyncio.to_thread(
                        lambda: open("product_urls.txt", "r", encoding="utf-8").read().splitlines()
                    )

                    total_products = len(lines)

                    for i, line in enumerate(lines, start=1):
                        line_url = line.strip()
                        if not line_url:
                            continue

                        print(f"Scraping product {i} out of {total_products}")

                        # Create CrawledUrl entity and persist it
                        crawled_url = CrawledUrl(
                            crawled_url_address=line_url,
                            website_id=website_id
                        )
                        self.__websiteService.addCrawledWebsiteUrl(crawled_url)

                        # Scrape the url to get the data
                        scraped_product_from_url = await self.__scraperService.scrapeURL(line_url)

                        # Create product with scraped data for the website
                        result = await asyncio.to_thread(
                            self.__scraperService.createProductWithScrapedData,
                            scraped_product_from_url,
                            website_id
                        )

                        # Persist the created product
                        self.__websiteService.addProduct(result)

                    '''
                    if results:
                        print("\nResults returned successfully!")
                        print(f"Total filtered URLs: {results['categorization']['total']}")
                        print(f"Product URLs: {results['categorization']['product_count']}")
                        print(f"Category URLs: {results['categorization']['category_count']}")
                    '''

                except Exception as e:
                    print(f"Error in main: {e}")
                    return None

            elif option == 2:
                websiteUrl = "https://www.bershka.com/ro/"
                website_id = self.__websiteService.getWebsiteByName(websiteUrl).id

                # Maybe make the URL to be given as input
                product_url = "https://www.bershka.com/ro/pulover-multicolor-cu-aspect-periat-c0p200458828.html?colorId=507"
                scraped_product_from_url = await self.__scraperService.scrapeURL(product_url)
                result = self.__scraperService.createProductWithScrapedData(scraped_product_from_url, website_id)

                print("The scraped product from the URL is:")
                print(result.toString())

            elif option == 3:
                #TODO: implement first dm technique
                pass

            elif option == 4:
                # TODO: implement second dm technique
                pass

            elif option == 5:
                exit(0)