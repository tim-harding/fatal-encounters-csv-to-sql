import os


SUBDIRS = ["datasets", "housing"]
TGZ_NAME = "housing.tgz"
CSV_NAME = "housing.csv"
URL_ROOT = f"https://raw.githubusercontent.com/ageron/handson-ml/master"
URL_HOUSING = f"{URL_ROOT}/{'/'.join(SUBDIRS)}/{TGZ_NAME}"
PATH_ROOT = os.path.join(os.getcwd(), *SUBDIRS)
TGZ_PATH = os.path.join(PATH_ROOT, TGZ_NAME)
CSV_PATH = os.path.join(PATH_ROOT, CSV_NAME)