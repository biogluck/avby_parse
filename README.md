# av.by parsing

## What this code does?

It parses website av.by, finds all Renault Duster with diesel engine and saves result to _csv_ file and to _sqlite_ database.

---

## Purpose of this "project"

Main purpose for me is to study/train Python libraries:

- BeautifulSoup
- sqlalchemy
- logging

---

## How to run this code

```
python parse_carsavby.py
```

To test database connection run

```
python database.py
```

It will connect database and print out all cars and prices with dates in it. If no DB exists, it will create it.

---

## Run this script daily

In file

```
/etc/anacrontab
```

Add line

```
@daily  5       daily.parse_av  python <path_to_script>/parse_carsavby.py
```

or

```
1  5       daily.parse_av  python <path_to_script>/parse_carsavby.py

```
