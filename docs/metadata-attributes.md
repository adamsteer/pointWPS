# Metadata attribute record for pointWPS

We expect pontWPS to obtain dataset boundaries and metadata from a data store - it is much faster than querying the raw data!

So - what do we expect the data store to ingest? And where does the metadata come from?

Here is a 'first cut' sample JSON record that we might find useful.

```
{
    "surveyname": "some_survey_id",
    "filename": "/full/path/to/file",
    "datatype" "[ las | laz | netCDF | pgsql]",
    "count": "123456789",
    "area": "349875",
    "mean_density": "10.34",
    "schema": {
              Storage schema - eg JSON blob result of 'pdal info --schema'. This helps answer a question like 'does this data have RGB points?', or 'are there special VLRs attached?'. It might also be the output of a query on a pgsql schema table for this dataset, or an ncdump -h.
              },
    "bbox": {
            "EPSG:4326": {
                "bbox"["minx", "miny", "maxx", "maxy" ],
                "boundary": "POLYGON or MULTIPOLYGON ((WKT))"
                }
            "native": {
            "bbox"["minx", "miny", "maxx", "maxy" ],
                "boundary": "POLYGON or MULTIPOLYGON ((WKT))"
                },
            },
    "srs": "OGC SRS WKT",
    "heightreference": "WGS84 | ITRF08 | AHD94 | GRS80", <-- ellipsoidal or orthometric height - and which one?
    "units": {
        "vertical": "m",
        "horizontal": "m"
        },
    "ASPRSclass" : { <-- if ASPRS classification data are present, show them here. If not, assign all points to '0'
        "0": 0,
        "1": 2345,
        "2": 9879,
        "3": 534634,
        "4": 87362,
        ...
        "18": 9875,
        "xx": yyy
    },
    "scale_x": 0.001, <-- these might be '1' for data stored as float
    "scale_y": 0.001,
    "scale_z": 0.001,
    "software_id": "LP360 from QCoherent Software  ",
    }
```

These data can be obtained with the following queries from PDAL:

```
pdal info --metadata /path/to/file
pdal info --boundary /path/to/file
pdal info --schema /path/to/file
pdal info --filters.stats.dimensions=Classification --filters.stats.count="Classification" /path/to/file
```

which can be compounded into:
```
pdal info --metadata --boundary --schema --filters.stats.dimensions=Classification --filters.stats.count="Classification" /path/to/file
```

As far as I can see the hardest thing to extract will be the survey name - since naming rules might not be consistent. For data in /g/data/rr1, and /d/data/ub8 a regular expression like:
```
^[a-zA-Z0-9].*_
```
...on the file name should be OK.

This query set takes ~1 minute per tile - for LAS data it is reading though the file itself, not just hitting a metadata entry. This, however, should be a one-time cost. Moving data should require only path updating.

## What do we want from a metadata store?

With all this data, what do we want to do?

It doesn't make sense to query metadata directly from LAS tiles. If we made them all into netCDFs, maybe an ncdump would do the trick - but with other costs (like how do we organise data?). Even if we used netCDF stores, it seems more efficient to query a metadata store in an optimised PostGIS database for things like:

- tell me what data exist in my region of interest
- tell me if my data have ground and tree classifications
- how dense are these data (ie how many points/m)
- what surveys exist in my ROI?
- show me all the files containing data in my ROI
- show me the distribution of point classes in my ROI

These types of queries exist in a data discovery space - users trying to find out what data exist where.

Moving one step away from direct queries, the metadata store underpins server-side processing which asks simpler questions like:
- intersect tile boundaries with an input geometry and return a list of file names
- as above, but limit by survey name or point density

This first-stage filter restricts the size of datasets that underlying processes need to work with.

## Issues we have found using a metadata store

SRS metadata are often incorrect or incomplete - which creates difficulty for downstream processing.

Using a similar data crawling scheme, a programmatic QA tool will be developed to catch errant metadata before datasets are published.
