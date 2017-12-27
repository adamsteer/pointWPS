#!/bin/bash
# what does this do?
#
# runs a PDAL pipeline to merge tile clippings into a single LAZ file
# must be run *after* tilehandler.sh

if [[ $# -lt 2 ]] ; then
    echo 'Please enter 2 arguments like:'
    echo '# sh ./merge_points.sh /path/to/workdir "outfilename"'
    exit 1
fi

workdir=$1
infilename=$2

#hopefully soon workdir will be not needed - we aim to assemble the parts in memory
echo $workdir
echo $infilename


out_path=$workdir/${infilename}_potree

echo $out_path
mkdir -p $out_path

#run potreeconverter
/local/build/potreeconverter-build/PotreeConverter/PotreeConverter -i $workdir/*.las -o $workdir/${infilename}_potree --material ELEVATION

cd $workdir

zip -r ${infilename}_potree.zip ${infilename}_potree

cd -


#pyWPS should clean up the work dir once the process finishes.
