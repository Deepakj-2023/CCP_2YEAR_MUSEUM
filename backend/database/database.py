import os
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,Session
from sqlalchemy_utils import create_database, database_exists

from database.models import Base
from dotenv import load_dotenv
load_dotenv()
class Database:
    _engine = None
    _session = None

    @staticmethod
    def init_engine():
        """
            initalizing database engine
        """
        if Database._engine is None:
            user = os.getenv("USERNAME")
            password = os.getenv("PASSWORD")
            print("USER IS :",user," password:",password)
            database_name = "museum_bookings_db"
            database_url = f"postgresql://{user}:{password}@localhost/{database_name}"
            Database._engine = create_engine(
                database_url,echo=False, pool_size = 10, max_overflow = 20
            )

        Database.init_db()
        return Database._engine
    
    @staticmethod
    def init_db():
        """to initalize the database
        """
        if not database_exists(Database.get_engine().url):
            create_database(Database.get_engine().url)

        Base.metadata.create_all(bind=Database.get_engine())

    @staticmethod
    def get_engine():
        if Database._engine is None:
            Database.init_engine()
        return Database._engine
    
    @staticmethod
    def get_session_maker():
        if Database._session is None:
            Database._session = sessionmaker(
                autocommit=False, autoflush=False, bind=Database.get_engine()
            )
        return Database._session
        

    @staticmethod
    def get_db() -> Generator[Session, None, None]:
        """
        Providing a database session using the pre-initialized sessionmaker
        """
        session_maker = Database.get_session_maker()
        session = session_maker()
        try:
            yield session
        finally:
            session.close()
            