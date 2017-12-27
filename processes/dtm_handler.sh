#!/bin/bash

# what does this do?
#
# globs a list of files to parallel, and invokes a shell script to do stuff
if [[ $# -lt  ]] ; then
    echo 'Please enter arguments like:'
    echo '# sh ./tilehandler.sh /path/to/workdir output_format survey_name "WKT polygon" 2 3.5 "comma separated list of outputs"'
    exit 1
fi

workdir=$1
outputdir=$2
write_format=$3
dataset=$4
files=$5
polygon=$6
resolution=$7
radius=$8
output_type=$9

#hopefully soon workdir will be not needed - we aim to assemble the parts in memory
echo $workdir
echo $files
echo $polygon
echo $resolution
echo $radius
#echo ""
echo ""

echo "splitting tasks and generating clipped tiles"


safecores=$(expr `parallel --number-of-cpus` - 2)

#run parallel on as many cores as we can consume without running out of memory
parallel -jsafecores sh /local/pywps/processes/pointclipper.sh $workdir {} $polygon ::: $files

#what to call the output file... hmm.

mergedfilename=$dataset"_clipped_dtm.tif"
#zipfilename=$dataset"_clipped_dtm.zip"

cat <<EOF >> $workdir/dtm_merge_pipeline.json
{
    "pipeline": [
        "$workdir/*_clipped.laz",
        {
            "type": "filters.range",
            "limits": "Classification[2:2]"
        },
        {
            "type": "writers.gdal",
            "resolution": $resolution,
            "radius": $radius,
            "gdaldriver": "GTiff",
            "output_type": $output_type,
            "filename":"$workdir/$mergedfilename"
        }
    ]
}
EOF


#need to work out an efficient way to add PDAL metadata from the point clip step to the VLR here. Maybe we could punch out a JSON pipeline and zip it with the output file?

cat $workdir/dtm_merge_pipeline.json

echo "Now merging results"

pdal pipeline $workdir/dtm_merge_pipeline.json

#cat 'processing report for dtm generation\n' > $workdir/processingreport.txt
#cat '----\n\n' >> $workdir/processingreport.txt

#cat 'files used:\n'  >> $workdir/processingreport.txt
#cat $files >> $workdir/processingreport.txt

#cat '\n----\n\n' >> $workdir/processingreport.txt
#cat $workdir/dtm_merge_pipeline.json >> $workdir/processingreport.txt

#zip -r  $workdir/$zipfilename $workdir/$mergedfilename $workdir/processingreport.txt

#pdal merge $workdir/*.laz $outputdir/$dataset"_clip.laz"

#pyWPS should clean up the work dir once the process finishes.