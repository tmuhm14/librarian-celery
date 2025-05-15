# db.py

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

metadata = MetaData()
Base = declarative_base()


def db_connect():
    username = os.getenv("DB_USERNAME")
    password = os.getenv("DB_PASSWORD")
    dbname = os.getenv("DB_NAME")
    port = os.getenv("DB_PORT")
    host = os.getenv("DB_HOST")

    engine = create_engine(
        f"postgresql://{username}:{password}@{host}:{port}/{dbname}", echo=False, pool_pre_ping=True)
    connection = engine.connect()

    return engine, connection


def create_tables(engine):
    metadata.drop_all(engine, checkfirst=True)
    metadata.create_all(engine, checkfirst=True)


def create_tables_orm(engine):
    Base.metadata.drop_all(engine, checkfirst=True)
    Base.metadata.create_all(engine, checkfirst=True)


def create_session(engine):
    Session = sessionmaker(bind=engine, expire_on_commit=False)
    session = Session()

    return session
