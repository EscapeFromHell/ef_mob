import os
from typing import Generator
from datetime import datetime

from bs4 import BeautifulSoup
import pandas as pd
import requests
from sqlalchemy import create_engine, Column, Integer, String, Date, DateTime
from sqlalchemy.orm import DeclarativeBase, sessionmaker


URL = "https://spimex.com"

sqlite_database = "sqlite:///spimex.db"
engine = create_engine(url=sqlite_database)
Session = sessionmaker(autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


class SpimexTradingResults(Base):
    __tablename__ = "spimex_trading_results"
    id = Column(Integer, primary_key=True)
    exchange_product_id = Column(String)
    exchange_product_name = Column(String)
    oil_id = Column(String)
    delivery_basis_id = Column(String)
    delivery_basis_name = Column(String)
    delivery_type_id = Column(String)
    volume = Column(Integer)
    total = Column(Integer)
    count = Column(Integer)
    date = Column(Date)
    created_on = Column(DateTime, default=datetime.now)
    updated_on = Column(DateTime, default=datetime.now, onupdate=datetime.now)


Base.metadata.create_all(engine)


class SpimexParser:
    """
    Класс для парсинга Spimex.com и извлечения результатов торгов.
    """
    def __init__(self, target_data: datetime) -> None:
        """
        Инициализирует класс SpimexParser.

        Args:
            target_data (datetime): Целевая дата для извлечения результатов торгов.
        """
        self.target_data = target_data

    @staticmethod
    def __remove_excel() -> None:
        """
        Удаляет файл oil_data.xls, если он существует.
        """
        if os.path.exists("oil_data.xls"):
            os.remove("oil_data.xls")

    @staticmethod
    def __add_to_db(objects: list[SpimexTradingResults]) -> None:
        """
        Добавляет список объектов SpimexTradingResult в базу данных.

        Args:
            objects (list[SpimexTradingResult]): Список объектов SpimexTradingResult для добавления.
        """
        session = Session()
        with session as db:
            db.add_all(objects)
            db.commit()
            db.close()

    @staticmethod
    def __get_date_from_url(url: str) -> datetime:
        """
        Получает дату из URL бюллетеня Spimex.

        Args:
            url (str): URL бюллетеня Spimex.

        Returns:
            datetime: Дата бюллетеня Spimex.
        """
        date_string = url.split("oil_xls_")[1]
        year = int(date_string[:4])
        month = int(date_string[4:6])
        day = int(date_string[6:8])
        date_in_url = datetime(year, month, day)
        return date_in_url

    @staticmethod
    def __download_spimex_bulletin(url: str) -> None:
        """
        Загружает бюллетень Spimex.

        Args:
            url (str): URL бюллетеня Spimex.

        Raises:
            Exception: Если произошла ошибка при загрузке бюллетеня.
        """
        try:
            response = requests.get(url=url)
            with open("oil_data.xls", "wb") as file:
                file.write(response.content)
        except (requests.ConnectionError, requests.ConnectTimeout, requests.HTTPError) as e:
            print(f"Ошибка при скачивании бюллетеня: {e}!")
            raise Exception

    @staticmethod
    def __parse_links_from_page(page: int) -> list[str]:
        """
        Разбирает ссылки со страницы Spimex.

        Args:
            page (int): Номер страницы Spimex.

        Returns:
            list[str]: Список ссылок на данной странице Spimex.
        """
        try:
            url = f"https://spimex.com/markets/oil_products/trades/results/?page=page-{page}]"
            response = requests.get(url)
            soup = BeautifulSoup(response.content, "html.parser")
            links = [link.get('href') for link in soup.find_all("a") if "/upload/reports/oil_xls/oil_xls" in str(link)]
            return links
        except (requests.ConnectionError, requests.ConnectTimeout, requests.HTTPError) as e:
            print(f"Ошибка при запросе: {e}!")
            raise Exception

    def __parse_links(self) -> list[str]:
        """
        Разбирает ссылки со страниц Spimex.

        Returns:
            list[str]: Список ссылок на бюллетени Spimex.
        """
        result = []
        flag = True
        page = 1
        while flag is True:
            links = self.__parse_links_from_page(page)
            if links:
                for link in links:
                    if self.__get_date_from_url(url=link) >= self.target_data:
                        result.append(link)
                    else:
                        flag = False
                        break
            else:
                flag = False
            page += 1
        return result

    @staticmethod
    def __get_data_from_excel() -> Generator:
        """
        Получает данные из файла Excel.

        Yields:
            Generator: Данные из файла Excel.
        """
        df = pd.read_excel("oil_data.xls")
        target = 0
        for index, row in df.iterrows():
            try:
                if "Единица измерения: Метрическая тонна" in row.iloc[1]:
                    target = index
            except TypeError:
                pass
        df = df.iloc[target + 2:]
        df = df.iloc[:-2, [1, 2, 3, 4, 5, -1]]
        df = df.replace("-", 0)
        df = df.fillna(0)
        result = df[df.iloc[:, -1].astype(int) > 0]
        for index, row in result.iterrows():
            yield row.tolist()

    def __prepare_objects(self, date: datetime) -> list[SpimexTradingResults]:
        """
        Подготавливает список объектов SpimexTradingResult из данных в файле Excel.

        Args:
            date (datetime): Дата бюллетеня Spimex.

        Returns:
            list[SpimexTradingResult]: Список объектов SpimexTradingResult.
        """
        objects = []
        for data in self.__get_data_from_excel():
            trading_result = SpimexTradingResults(
                exchange_product_id=data[0],
                exchange_product_name=data[1],
                oil_id=data[0][:4],
                delivery_basis_id=data[0][4:7],
                delivery_basis_name=data[2],
                delivery_type_id=data[0][-1],
                volume=data[3],
                total=data[4],
                count=data[5],
                date=date
            )
            objects.append(trading_result)
        return objects

    def start_process(self) -> None:
        """
        Начинает процесс парсинга Spimex и добавления результатов торгов в базу данных.
        """
        try:
            print("Выполнение...")
            files = self.__parse_links()
            for file in files:
                self.__download_spimex_bulletin(url=f"{URL}{file}")
                date = self.__get_date_from_url(url=file)
                objects = self.__prepare_objects(date=date)
                self.__add_to_db(objects=objects)
                self.__remove_excel()
        except Exception as e:
            print(f"Возникла ошибка при выполнении! {e}")
        else:
            print("Выполнение завершено!")


if __name__ == "__main__":
    sp = SpimexParser(datetime(2023, 1, 1))
    sp.start_process()
