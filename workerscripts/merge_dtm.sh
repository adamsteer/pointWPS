#!/bin/bash
# what does this do?
#
# runs a PDAL pipeline to merge tile clippings into a single LAZ file
# must be run *after* tilehandler.sh

if [[ $# -lt 5 ]] ; then
    echo 'Please enter 6 arguments like:'
    echo '# sh ./merge_dtm.sh /path/to/workdir resolution radius output_layers gdal_driver outfilename'
    exit 1
fi

workdir=$1
resolution=$2
radius=$3
output_type=$4
gdal_driver=$5
outfilename=$6

echo "out file name:"
echo $outfilename

echo "work dir:"
echo $workdir
echo "-----------------"

cat <<EOF >> $workdir/dtm_merge_pipeline.json
{
    "pipeline": [
        "$workdir/*_clipped.las",
        {
            "type": "filters.range",
            "limits": "Classification[2:2]"
        },
        {
            "type": "writers.gdal",
            "resolution": $resolution,
            "radius": $radius,
            "gdaldriver": "${gdal_driver}",
            "output_type": "${output_type}",
            "filename":"$workdir/${outfilename}"
        }
    ]
}
EOF

#need to work out an efficient way to add PDAL metadata from the point clip step to the VLR here. Maybe we could punch out a JSON pipeline and zip it with the output file?

#use journalctl -f on CentOS to see this output
cat $workdir/dtm_merge_pipeline.json

echo "Now merging results"

pdal pipeline $workdir/dtm_merge_pipeline.json

echo "done!"