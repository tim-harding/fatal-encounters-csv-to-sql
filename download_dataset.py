import os
import tarfile
from six.moves import urllib
from chapter import paths

def main():
    if not os.path.isdir(paths.PATH_ROOT):
        os.makedirs(paths.PATH_ROOT)
    urllib.request.urlretrieve(paths.URL, paths.FILEPATH)

main()