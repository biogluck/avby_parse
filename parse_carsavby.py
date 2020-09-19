import csv
import logging
import urllib
from datetime import date
from pathlib import Path

from typing import Optional

import requests
from bs4 import BeautifulSoup, element

from database import Car, CarPrice, load_session


def get_html(url: str) -> bytes:
    r = requests.get(url)
    return r.content


def write_to_file(file: str, data: dict, keys: dict) -> None:
    with open(file, "a") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)


def parse_item(item: element.Tag) -> dict:
    item_title_el = item.find("div", class_="listing-item-title")
    title = item_title_el.h4.a.text.strip()
    link = item_title_el.h4.a.get("href")
    car_id = link.split("/")[-1]
    item_price_el = item.find("div", class_="listing-item-price")
    year = int(item_price_el.span.text.strip())
    price = item_price_el.small.text.strip().replace(" ", "").replace("р.", "")
    item_desc_el = item.find("div", class_="listing-item-desc")
    distance = item_desc_el.text.strip().split(",")[-1].replace("км", "").strip()
    parse_date = date.today()
    car_data = {
        "id": car_id,
        "title": title,
        "link": link,
        "year": year,
        "price": price,
        "distance": distance,
        "date": parse_date,
    }
    return car_data


def get_items(url: str):
    """
    Function for getting items on page.

    :param url: url of page to get items
    :return: tuple(items: list, next_link: str)
    """
    next_link: Optional[str] = None
    html = get_html(url)
    soup = BeautifulSoup(html, "lxml")
    items = soup.findAll("div", class_="listing-item")
    # там 2 линки на предыдущую и следующую. Фильтруем только следующую.
    links = soup.findAll("a", class_="pages-arrows-link")
    links = [l for l in links if "Следующая страница" in l.text]
    if links:
        next_link = links[0].get("href")
    return (items, next_link)


def parse_page(url: str):
    items, next_link = get_items(url)
    while next_link:
        next_items, next_link = get_items(next_link)
        items.extend(next_items)
    return items


def main():
    wdir = Path(__file__).resolve(strict=True).parent
    logging.basicConfig(
        filename=f"{wdir}/parselog.log",
        format="%(asctime)s : %(levelname)s : %(message)s",
        level=logging.INFO,
    )
    logging.info(f"Parsing av.by started")
    session = load_session(wdir)
    csv_file = f"{wdir}/csv/test-{date.today()}.csv"
    url_params = {
        "brand_id[0]": 1039,
        "model_id[0]": 2281,
        "generation_id[0]": 0,
        "currency": "USD",
        "engine_type": 2,
        "sort": "year",
        "order": "desc",
    }
    url_base = "https://cars.av.by/search?"

    url = url_base + urllib.parse.urlencode(url_params)
    # the next line is for test
    # url = 'https://cars.av.by/renault/duster'
    fields = (
        "id",
        "title",
        "link",
        "year",
        "price",
        "distance",
        "date",
    )

    items = parse_page(url)
    item_dicts = []
    for item in items:
        item_dict = parse_item(item)
        item_dicts.append(item_dict)
        car = session.query(Car).filter(Car.id == item_dict["id"]).one_or_none()
        if not car:
            logging.info(f'New car item with id: {item_dict["id"]}!')
            car = Car(
                id=item_dict["id"],
                title=item_dict["title"],
                link=item_dict["link"],
                year=item_dict["year"],
                distance=item_dict["distance"],
            )
            car_price = CarPrice(price=item_dict["price"], date=item_dict["date"],)
            car.prices.append(car_price)
            session.add(car)
        else:
            if car.prices[-1].price != int(item_dict["price"]):
                logging.info(f'New price for car with id: {item_dict["id"]}!')
                car_price = CarPrice(price=item_dict["price"], date=date.today(),)
                car.prices.append(car_price)
    session.commit()
    write_to_file(csv_file, item_dicts, fields)
    logging.info(f"Parsing av.by finished")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(e)
