from sqlalchemy import text
from database import Database

class TransactionRepository:
    def __init__(self):
        self.__db = Database()


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