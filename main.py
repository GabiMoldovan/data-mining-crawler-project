from service.scraperService import ScraperService
import asyncio

async def main():
    scraper = ScraperService()

    test_url = "https://www.bershka.com/ro/hanorac-oversize-fermoar-glug%C4%83-c0p193051059.html?colorId=717"

    result = await scraper.scrapeURL(test_url)

    print(result)

if __name__ == "__main__":
    asyncio.run(main())