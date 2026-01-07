from sqlalchemy import text
from database import Database, Base
from model import CrawledUrl
from model.product import Product
from model.website import Website


class TransactionRepository:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(TransactionRepository, cls).__new__(cls)
        return cls._instance


    def __init__(self):
        if hasattr(self, "_initialized") and self._initialized:
            return

        self.__db = Database()
        self._initialized = True


    def getRegressionData(self):
        """
            Fetches data suitable for Price Prediction Regression
        """
        with self.__db.session() as session:
            query = text("""
                SELECT product_price as price,
                    product_name as name,
                    COALESCE(product_extra_info, '') as extra_info,
                    COALESCE(product_reference_text, '') as ref_info
                FROM product
                WHERE product_price IS NOT NULL
            """)
            result = session.execute(query)
            return [dict(row._mapping) for row in result.fetchall()]