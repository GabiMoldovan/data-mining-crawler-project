from database import Database

class WebsiteRepository:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(WebsiteRepository, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized") and self._initialized:
            return

        self.__db = Database()
        self.__session = self.__db.get_session()
        self._initialized = True

