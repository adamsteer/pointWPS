#!/bin/bash

#what does pointclipper do?
# we assume here that an upstream process provides a tile name and full path
# and a polygon to clip with.

# all we do here is clip a single data source file and write out a file with the result
# we ask for a workdir, this will get passed from pywps, which runs the parent process

# upstream of here, we use parallels to clip multiple datasets at the same time for
# merging in a downstream process. SO we track tile names through until the merge.

# here, if we don't clean up we should have N json files and N little clipped point
# files, where N is the number of tiles which intersect the provided geometry

workdir=$1
t_path=$2
tilepath=${t_path//\"/}
polygon=$3

echo $workdir
echo $tilepath
echo $polygon

tile=$(basename "$tilepath" .las)
outfilename=$tile"_clipped.las"

echo $tile

cat <<EOF >> $workdir/$tile"_pipeline.json"
{
    "pipeline": [
        "$tilepath",
        {
            "type": "filters.crop",
            "polygon": "$polygon"
        },
        {
            "type": "writers.las",
            "filename":"$workdir/$outfilename"
        }
    ]
}
EOF

cat $workdir/$tile"_pipeline.json"

pdal pipeline $workdir/$tile"_pipeline.json"

#clean up - when we know things work.
rm -rf $workdir/$tile"_pipeline.json"
