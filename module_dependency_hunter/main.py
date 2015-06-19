#-*- coding: utf-8 -*-
"""
Parse source code to determine what files import a given module. This should help
engineers determine where coverage needs to be applied for integration testing.
"""
from .ast_walker import parse_python_source

import os
#import sys
import pprint


def find_pyfiles(path):
    """Find the py files in the path"""
    dir_files = []
    path_dir = os.path.abspath(path)
    if os.path.exists(path_dir) and os.path.isdir(path_dir):
        for root, _, path_files in os.walk(path_dir):
            for path_file in path_files:
                _, ext = os.path.splitext(path_file)
                if ext == '.py':
                    dir_files.append([root, path_file])
    return dir_files

def find_imports(start_path):
    """Traverse the path and find imports"""
    for path_dir, path_file in find_pyfiles(start_path):
        modules = parse_python_source(os.path.join(path_dir, path_file))

        if modules:
            print os.path.join(path_dir, path_file)
            for mod in modules:
                print "\t{}".format(mod)
        print ""

    return True

def main():
    """main runner method"""
    moduleslist = find_imports(r'/opt/pythonenv/v2_ordergroove-py27/v2/api/customer')
    pprint.pprint(moduleslist)

if __name__ == '__main__':
    main()
