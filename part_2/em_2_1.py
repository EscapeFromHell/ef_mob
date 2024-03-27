import typing as t

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import relationship, sessionmaker

DATABASE_DSN = 'postgresql+psycopg2://username:password@5432/dbname'

class_registry: t.Dict = {}


@as_declarative(class_registry=class_registry)
class Base:
    id: t.Any
    __name__: str

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


class Genre(Base):
    id = Column(Integer, primary_key=True)
    name = Column(String)
    books = relationship("Book", back_populates="genre")


class Author(Base):
    id = Column(Integer, primary_key=True)
    name = Column(String)
    books = relationship("Book", back_populates="author")


class Book(Base):
    id = Column(Integer, primary_key=True)
    title = Column(String)
    price = Column(Integer)
    quantity = Column(Integer)
    genre_id = Column(Integer, ForeignKey('genre.id'))
    author_id = Column(Integer, ForeignKey('author.id'))
    genre = relationship("Genre", back_populates="books")
    author = relationship("Author", back_populates="books")


class City(Base):
    id = Column(Integer, primary_key=True)
    name = Column(String)
    delivery_time = Column(DateTime)
    clients = relationship("Client", back_populates="city")


class Client(Base):
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    city_id = Column(Integer, ForeignKey('city.id'))
    city = relationship("City", back_populates="clients")
    buys = relationship("Buy", back_populates="client")


class Buy(Base):
    id = Column(Integer, primary_key=True)
    wishes = Column(String)
    client_id = Column(Integer, ForeignKey('client.id'))
    client = relationship("Client", back_populates="buys")
    buy_books = relationship("BuyBook", back_populates="buy")
    buy_steps = relationship("BuyStep", back_populates="buy")


class BuyBook(Base):
    id = Column(Integer, primary_key=True)
    quantity = Column(Integer)
    book_id = Column(Integer, ForeignKey('book.id'))
    buy_id = Column(Integer, ForeignKey('buy.id'))
    book = relationship("Book", back_populates="buy_books")
    buy = relationship("Buy", back_populates="buy_books")


class Step(Base):
    id = Column(Integer, primary_key=True)
    name = Column(String)
    buy_steps = relationship("BuyStep", back_populates="step")


class BuyStep(Base):
    id = Column(Integer, primary_key=True)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    buy_id = Column(Integer, ForeignKey('buy.id'))
    step_id = Column(Integer, ForeignKey('step.id'))
    buy = relationship("Buy", back_populates="buy_steps")
    step = relationship("Step", back_populates="buy_steps")


engine = create_engine(DATABASE_DSN)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
