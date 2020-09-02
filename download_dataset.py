import os
import tarfile
from six.moves import urllib
from chapter import paths

def main():
    if not os.path.isdir(paths.PATH_ROOT):
        os.makedirs(paths.PATH_ROOT)
    urllib.request.urlretrieve(paths.URL_HOUSING, paths.TGZ_PATH)
    housing_tgz = tarfile.open(paths.TGZ_PATH)
    housing_tgz.extractall(path=paths.PATH_ROOT)
    housing_tgz.close()

main()