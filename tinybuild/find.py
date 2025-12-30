import fnmatch
import os
import pathlib
import re


def find_files(folder, includes=['*'], excludes=['.*', '*/.*']):
    include = re.compile('|'.join(fnmatch.translate(x) for x in includes))
    exclude = re.compile('|'.join(fnmatch.translate(x) for x in excludes))
    filenames = scan_folder(folder, include, exclude)
    filenames = [pathlib.Path(x) for x in filenames]
    filenames = sorted(list(filenames))
    return filenames
