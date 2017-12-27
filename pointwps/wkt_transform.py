"""
A simple function for transforming WKT geometries

Adapted from:
http://toblerity.org/shapely/manual.html#shapely.ops.transform

Adam Steer, NCI, July 2017
"""
from functools import partial

from shapely.ops import transform
from shapely.wkt import loads
from shapely.wkt import dumps

import pyproj

def transformwkt(wkt, in_srs, out_srs):
    in_epsg = 'EPSG:'+str(in_srs)
    out_epsg = 'EPSG:'+str(out_srs)
    
    project = partial(
        pyproj.transform,
        pyproj.Proj(init=in_epsg),
        pyproj.Proj(init=out_epsg))

    #wkt to geometry 
    in_wkt=loads(wkt)
    out_wkt = transform(project, in_wkt)
    return(out_wkt)

if __name__ == '__main__':
    main()