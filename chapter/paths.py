import os


SUBDIRS = ["datasets", "mapping_police_violence"]
FILENAME = "fatal_encounters.xlsx"
# URL = f"https://mappingpoliceviolence.org/s/{FILENAME}"
PATH_ROOT = os.path.join(os.getcwd(), *SUBDIRS)
FILEPATH = os.path.join(PATH_ROOT, FILENAME)