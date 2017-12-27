"""
Remapping filesystem paths

Adam Steer, July 2017

Declare a path map for exposing files to the public. Using the dictionary below,
system paths on the right (dictionary values) are replaced with aliases on the left
(dictionary keys). Some care may be needed to map longer or shorter paths, not
tested with all possibilities.

At some point the path mapping should be removed from this function and places in a
configuration directive
"""

import os

PATHMAPS = {
            "project_key": "/path/to/project",
            }

def remap_path(path):
    """
    Map from filesystem paths to something else, using the path map to determine how to
    proceeed. Here, we substitute real paths (values) with shortened paths (keys).

    The idea is to try and retain enough information that a user could find the dataset
     via other pubishing methods if available, but not know about system structure.
    """

    if not os.path.isabs(path) or path.find('..') > -1:
        raise ValueError("Path must be absolute: {}".format(path))

    pathbits = path.split(os.sep)

    if pathbits[3] in PATHMAPS:
        keybits = PATHMAPS[pathbits[3]].split(os.sep)
        pathroot=pathbits[3]
    else:
        raise ValueError("Path is unrecognised: {}".format(path) )

    public_path = '/'+ os.path.join(pathroot,*pathbits[len(keybits):])

    return(public_path)

def unmap_path(path):
    """
    Map from aliased paths to filesystem paths, using the path map to determine how to
    proceeed. Here, we substitute shortened paths (keys) with real paths (values).
    """
    if not os.path.isabs(path) or path.find('..') > -1:
        raise ValueError("Path must be absolute: {}".format(path))

    pathbits = path.split(os.sep)

    if pathbits[1] in PATHMAPS:
        system_path = os.path.join(PATHMAPS[pathbits[1]],*pathbits[2:])
    else:
        raise ValueError("Path is unrecognised: {}".format(path) )

    return(system_path)
