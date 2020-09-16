import os
from chapter import paths
import matplotlib.pyplot as plot
import xlrd
import datetime
import time
import psycopg2
from psycopg2.extras import execute_values
from psycopg2.extensions import adapt, register_adapter, AsIs


class City:
    def __init__(self, name, state_id):
        self.name = name
        self.state_id = state_id

    def __str__(self):
        return f"{self.name}, {self.state_id}"

    def __eq__(self, other):
        return self.name == other.name and self.state_id == other.state_id

    def __hash__(self):
        return hash(self.name) + hash(self.state_id)


class State:
    def __init__(self, shortname, name):
        self.shortname = shortname
        self.name = name

    def __str__(self):
        return self.shortname

    def __eq__(self, other):
        return self.shortname == other.shortname

    def __hash__(self):
        return hash(self.shortname)


class Position:
    def __init__(self, lat, long):
        self.lat = lat
        self.long = long
    

def adapt_position(position):
    lat = position.lat
    long = position.long
    return AsIs("'(%s, %s)'" % (long, lat))

def main():
    register_adapter(Position, adapt_position)

    workbook = xlrd.open_workbook(paths.FILEPATH)
    worksheet = workbook.sheet_by_index(0)

    races = {}
    cities = {}
    counties = {}
    agencies = {}
    causes = {}
    use_of_force = {}

    states_list = [
        "AL Alabama",
        "AK Alaska",
        "AZ Arizona",
        "AR Arkansas",
        "CA California",
        "CO Colorado",
        "CT Connecticut",
        "DE Delaware",
        "FL Florida",
        "GA Georgia",
        "HI Hawaii",
        "ID Idaho",
        "IL Illinois",
        "IN Indiana",
        "IA Iowa",
        "KS Kansas",
        "KY Kentucky",
        "LA Louisiana",
        "ME Maine",
        "MD Maryland",
        "MA Massachusetts",
        "MI Michigan",
        "MN Minnesota",
        "MS Mississippi",
        "MO Missouri",
        "MT Montana",
        "NE Nebraska",
        "NV Nevada",
        "NH New Hampshire",
        "NJ New Jersey",
        "NM New Mexico",
        "NY New York",
        "NC North Carolina",
        "ND North Dakota",
        "OH Ohio",
        "OK Oklahoma",
        "OR Oregon",
        "PA Pennsylvania",
        "RI Rhode Island",
        "SC South Carolina",
        "SD South Dakota",
        "TN Tennessee",
        "TX Texas",
        "UT Utah",
        "VT Vermont",
        "VA Virginia",
        "WA Washington",
        "DC Washington DC",
        "WV West Virginia",
        "WI Wisconsin",
        "WY Wyoming",
    ]

    states = {}
    for ident in states_list:
        split = ident.split()
        shortname = split[0]
        name = " ".join(split[1:])
        state = State(shortname, name)
        states[state] = len(states)

    people = []

    tic = time.perf_counter()

    for row in range(1, worksheet.nrows - 1):
        def val(col):
            return worksheet.cell_value(row, col)

        def id_or_next(collection, item):
            if not item in collection:
                collection[item] = len(collection)
            return collection[item]

        def id(collection, col):
            string = val(col)
            if string == "":
                return None
            return id_or_next(collection, string)

        def some_or_none(col):
            raw = val(col)
            return None if raw == "" else raw

        def int_or_none(col):
            raw = val(col)
            try:
                return int(raw)
            except:
                return None

        def name():
            raw = val(1)
            if raw == "Name withheld by police":
                return None
            return simplify_name(raw)

        def is_male():
            return val(3) == "Male"

        def race():
            return id(races, 4)

        def race_with_imputations():
            return id(races, 5)

        def imputation_probability():
            raw = val(6)
            return raw if isinstance(raw, float) else None

        def date():
            raw = val(8)
            date_tuple = xlrd.xldate_as_tuple(raw, workbook.datemode)
            return datetime.datetime(*date_tuple)

        def city():
            name = val(10)
            name = name.strip()
            if name == "":
                return None
            state_shortname = val(11)
            state_id = states[State(state_shortname, "")]
            city = City(name, state_id)
            return id_or_next(cities, city)

        def coordinate():
            return Position(val(15), val(16))

        person = {
            "id": int(val(0)),
            "name": name(),
            "age": int_or_none(2),
            "is_male": is_male(),
            "race": race(),
            "race_with_imputations": race_with_imputations(),
            "imputation_probability": imputation_probability(),
            "image_url": some_or_none(7),
            "date": date(),
            "address": some_or_none(9),
            "city": city(),
            "zipcode": int_or_none(12),
            "county": id(counties, 13),
            "coordinate": coordinate(),
            "agency": id(agencies, 17),
            "cause": id(causes, 18),
            "description": some_or_none(19),
            "use_of_force": id(use_of_force, 21),
            "article_url": some_or_none(22),
            "video_url": some_or_none(24),
        }

        people.append(person)

    toc = time.perf_counter()
    print(f"Parsed table in {toc - tic:0.4f} seconds")

    info = {
        "people": people,
        "cities": cities,
        "states": states,
        "tables": {
            "race": races,
            "county": counties,
            "agency": agencies,
            "cause": causes,
            "use_of_force": use_of_force,
        }
    }

    add_to_database(info)


def add_to_database(info):
    connect_string = "dbname=fatal_encounters user=postgres password=postgres"
    conn = psycopg2.connect(connect_string)
    cur = conn.cursor()

    cur.execute("DELETE FROM state")
    values = [(id, state.shortname, state.name)
              for state, id in info["states"].items()]
    query = "INSERT INTO state (id, shortname, name) VALUES %s"
    execute_values(cur, query, values)

    cur.execute("DELETE FROM city")
    values = [(id, city.name, city.state_id)
              for city, id in info["cities"].items()]
    query = "INSERT INTO city (id, name, state_id) VALUES %s"
    execute_values(cur, query, values)

    for table, rows in info["tables"].items():
        cur.execute(f"DELETE FROM {table}")
        query = f"INSERT INTO {table} (name, id) VALUES %s"
        execute_values(cur, query, rows.items())

    query = """
        INSERT INTO incident (
            id,
            name,
            age,
            is_male,
            race_id,
            race_with_imputations_id,
            imputation_probability,
            image_url,
            date,
            address,
            city_id,
            zipcode,
            county_id,
            latitude,
            longitude,
            agency_id,
            cause_id,
            description,
            use_of_force_id,
            article_url,
            video_url
        ) VALUES %s
    """
    values = [person_to_row(person) for person in info["people"]]
    cur.execute("DELETE FROM incident")
    execute_values(cur, query, values)

    conn.commit()
    cur.close()
    conn.close()


def person_to_row(person):
    return (
        person["id"],
        person["name"],
        person["age"],
        person["is_male"],
        person["race"],
        person["race_with_imputations"],
        person["imputation_probability"],
        person["image_url"],
        person["date"],
        person["address"],
        person["city"],
        person["zipcode"],
        person["county"],
        person["coordinate"].lat,
        person["coordinate"].long,
        person["agency"],
        person["cause"],
        person["description"],
        person["use_of_force"],
        person["article_url"],
        person["video_url"],
    )


def simplify_name(raw):
    full = raw.split(" aka")[0]
    parts = [part for part in full.split() if part[0] != "\""]
    return " ".join(parts)


main()
