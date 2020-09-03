import os
from chapter import paths
import matplotlib.pyplot as plot
import xlrd
import datetime


class City:
    def __init__(self, city_id, state_id):
        self.city_id = city_id
        self.state_id = state_id


class Name:
    def __init__(self, raw):
        if raw == "Name withheld by police":
            return None
        full = raw.split("aka")[0]
        parts = full.split()
        self.first = parts[0]
        self.last = parts[-1]
        if "Jr" in self.last:
            self.last = f"{parts[-2]} {self.last}"
        middle_parts = []
        for part in parts[1:-1]:
            if part[0] != "\"":
                middle_parts.append(part)
        self.middle = " ".join(middle_parts)


def main():
    workbook = xlrd.open_workbook(paths.FILEPATH)
    worksheet = workbook.sheet_by_index(0)

    # for col in range(worksheet.ncols):
    #     column_name = worksheet.cell_value(0, col)
    #     print(f"{col}: {column_name}")

    races = {}
    cities = {}
    states = {}
    counties = {}
    agencies = {}
    causes = {}
    use_of_force = {}

    for row in range(1, worksheet.nrows):
        def val(col):
            return worksheet.cell_value(row, col)

        def id(collection, col):
            string = val(col)
            if not string in collection:
                collection[string] = len(collection)
            return collection[string]

        def some_or_none(col):
            raw = val(col)
            return None if raw == "" else raw

        def int_or_none(col):
            raw = int(val(col))
            try:
                return int(raw)
            except:
                return None

        def name():
            raw = val(1)
            return Name(raw)
            

        def is_male():
            return val(3) == "Male"

        def race():
            return id(races, 4)

        def race_with_imputations():
            return id(races, 5)

        def imputation_probability():
            raw = val(6)
            if raw == "Not imputed":
                return None
            else:
                return raw

        def date():
            raw = val(8)
            date_tuple = xlrd.xldate_as_tuple(raw, workbook.datemode)
            return datetime.datetime(*date_tuple)

        def city():
            city_id = id(cities, 10)
            state_id = id(states, 11)
            return City(city_id, state_id)

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
            "latitude": val(15),
            "longitude": val(16),
            "agency": id(agencies, 17),
            "cause": id(causes, 18),
            "description": some_or_none(19),
            "use_of_force": id(use_of_force, 21),
            "article_link": some_or_none(22),
            "video": some_or_none(24),
        }

        for key, value in person.items():
            print(f"{key}: {value}")

        return


    print(races)


main()
