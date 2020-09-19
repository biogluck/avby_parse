from pathlib import Path

from sqlalchemy import Column, Date, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker


Base = declarative_base()


class Car(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True)
    title = Column(String(250), nullable=False)
    link = Column(String(250), nullable=False)
    year = Column(Integer)
    distance = Column(Integer)

    prices = relationship("CarPrice", back_populates="car")

    def __repr__(self):
        return f"<Car(title='{self.title}', year='{self.year}')>"


class CarPrice(Base):

    __tablename__ = "car_prices"

    id = Column(Integer, primary_key=True)
    car_id = Column(Integer, ForeignKey("cars.id"), nullable=False)
    price = Column(Integer)
    date = Column(Date)

    car = relationship("Car", back_populates="prices")

    def __repr__(self):
        return "<CarPrice(id='%s', price='%s', date='%s')>" % (
            self.id,
            self.price,
            self.date,
        )


def load_session(wdir: str):
    """"""
    DB_FILE = Path(wdir).joinpath("dusteravby.sqlite")
    engine = create_engine(f"sqlite:///{DB_FILE}", echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def main():
    BASE_DIR = Path(__file__).resolve(strict=True).parent
    session = load_session(BASE_DIR)
    # создает экземпляр create_engine
    # engine = create_engine('sqlite:///dusteravby.sqlite', echo=True)
    # Base.metadata.create_all(engine)  # Car.metadata.create_all(engine)
    # Session = sessionmaker(bind=engine)
    # session = Session()
    # car = Car(title="title",
    #           link="link",
    #           year=2016,
    #           price=10000,
    #           distance=100000,
    #           date=date(2020, 9, 9)
    #           )
    # print(car)
    # session.add(car)
    # session.commit()
    query = session.query(Car).order_by(-Car.year)
    print(query.count())
    for instance in query:
        print(instance.title, instance.year)
        for price in instance.prices:
            print(f"    {price.date}: {price.price}")


if __name__ == "__main__":
    main()
