# pointWPS

Is a set of WPS processes for delivering data and derived products from dense, ungridded point clouds. It was developed to technology demonstration (current state) for the National Computational Infrastructure.

## Current status

It is currently a set of hopefully-useful tools for reference. While the WPS parts may be useful, it would be unwise to deploy this system in it's current state into production. The system was described at EGU 2017, and FOSS4G (Boston) 2017, at which point a working demonstration was made available. The technology demonstration was decommissioned in around October 2017.

## Future hopes

The concept of on-demand products from point cloud data is gaining traction. The material here will be recycled in a more flexible architecture which better exploits much of the functionality offered by modern cloud platforms. Whatever can be made open source will be committed to this repository.

## Why does this exist?

NCI held > 30TB of LAS tiles, and were acquiring other point data collections as NetCDF files and other formats. These were currently published essentially as download-only services.

Point data services exist (http://opentopography.org), but did not meet NCI's diverse data requirements. Further, users were still required to obtain data in squares.

Users of dense point data have the following complaints:
- I need to download too much data
- Data arrive in formats I don't understand
- I need to do N processing steps to get the product I need
- I can't explore data before downloading it to see if it is what I need

The aim of this project is to provide solutions to as many of these complaints as possible:
- data clipping with complex polygons
- on-the-fly generation of derived products:
    - raster DTMs
    - rasterised height-above-ground
    - tree cover %
    - building %
    - potentially tree crown volume (awaiting algorithms for this work)
- data querying

Importantly, this was one attempt at using data as it is stored, and in an open, well-described and extensible way.

## requirements

The current development state needs:

- pyWPS (pyWPS v4.0): a python implementation for the OGC WPS service, describing client/server transactions. Chosen because there is a standard and well described way to write WPS processes in Python
- PDAL: the Point Data Abstraction Library, basically GDAL for points - translation, manipulation. Chosen because of it's multiple format read/write capacity, plus integration into C code later
- GDAL: underpins PDAL
- postgres-pointcloud: point data handling for postGIS, also an export format for PDAL
- netCDF/HDF
- WSGI: the Apache python interpreter
- GNU parallel

## Documentation

See [installation documentation](./docs/install.md); and what the pointWPS system expects from [a metadata attribute service](./docs/MASattributes.md).
