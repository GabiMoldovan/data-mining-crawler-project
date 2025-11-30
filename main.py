from model.website import Website
from model.product import Product
from database.database import Database
from repository.websiteRepository import WebsiteRepository
from service.websiteService import WebsiteService

if __name__ == '__main__':
    print('Goodbye, world!')

    websiteRepository = WebsiteRepository()
    websiteService = WebsiteService(websiteRepository)

    '''
    # Example on how to use the website service

    site = Website(website_name="Test Shop")
    
    websiteService.createWebsite(site)
    
    p1 = Product(product_name="Laptop", price=4999, website_id=site.id)
    p2 = Product(product_name="Mouse", price=99, website_id=site.id)

    websiteService.addProduct(p1)
    websiteService.addProduct(p2)
    '''


    '''
    # Example to insert data into database
    # Inserting data will be managed by the repositories
    database = Database()

    session = database.get_session()

    site = Website(website_name="Test Shop")
    p1 = Product(product_name="Laptop", price=4999)
    p2 = Product(product_name="Mouse", price=99)
 
    site.products.append(p1)
    site.products.append(p2)

    session.add(site)
    session.commit()
    '''
