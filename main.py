import pandas
import os
from chapter import paths

def main():
    housing = load_housing_data()
    housing.head()

def load_housing_data():
    return pandas.read_csv(paths.CSV_PATH)

main()