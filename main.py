from model.website import Website
from model.product import Product
from database.database import Database, Base
from model import *

if __name__ == '__main__':
    print('Goodbye, world!')

    '''
    # Creating tables
    database = Database()
    engine = database.engine
    Base.metadata.create_all(engine)


    # Inserting data
    session = database.get_session()

    site = Website(website_name="Test Shop")
    p1 = Product(product_name="Laptop", price=4999)
    p2 = Product(product_name="Mouse", price=99)

    site.products.append(p1)
    site.products.append(p2)

    session.add(site)
    session.commit()
    '''
