#!/bin/bash

# what does this do?
#
# runs a PDAL pipeline to merge several point chunks into one file

if [[ $# -lt 4 ]] ; then
    echo 'Please enter 4 arguments like:'
    echo '# sh ./merge_hag.sh /path/to/workdir output_format "filter string" "dataset"'
    exit 1
fi

workdir=$1
write_format=$2
pointfilter=$3
dataset=$4

#hopefully soon workdir will be not needed - we aim to assemble the parts in memory
echo $workdir

#what to call the output file... hmm.

mergedfilename=$dataset"_clipped_hag.laz"

cat <<EOF > $workdir/merge_pipeline.json
{
    "pipeline": [
        "$workdir/*_clipped.laz",
        {
            "type":"filters.hag"
        },
        {
            "type":"filters.ferry",
            "dimensions":"HeightAboveGround = Z"
        },
        {
            "type": "filters.range",
            "limits": "$pointfilter"
        },
        {
            "type": "writers.las",
            "forward": "all",
            "pdal_metadata":"true",
            "filename":"$workdir/$mergedfilename"
        }
    ]
}
EOF


#need to work out an efficient way to add PDAL metadata from the point clip step to the VLR here. Maybe we could punch out a JSON pipeline and zip it with the output file?

cat $workdir/merge_pipeline.json

pdal pipeline $workdir/merge_pipeline.json

#pdal merge $workdir/*.laz $outputdir/$dataset"_clip.laz"

#pyWPS should clean up the work dir once the process finishes.
