#!/bin/bash
# what does this do?
#
# globs a list of files to parallel, which runs a PDAL process to clip LAS/LAZ tiles
# using a supplied WKT polygon.
# transformation to the correct CRS for the LAS/LAZ dataset should have already
# taken place

if [[ $# -lt 3 ]] ; then
    echo 'Please enter 3 arguments like:'
    echo '# sh ./tilehandler.sh /path/to/workdir "space separated list of files" "WKT polygon"'
    exit 1
fi

workdir=$1
files=$2
polygon='"'$3'"'

#hopefully soon workdir will be not needed - we aim to assemble the parts in memory
echo $workdir
echo $files
echo $polygon

safecores=$(expr `parallel --number-of-cpus` - 2)

#run parallel on as many cores as we can consume without running out of memory
parallel -j$safecores sh /local/pointwps/workerscripts/pointclipper.sh $workdir {} $polygon ::: $files
