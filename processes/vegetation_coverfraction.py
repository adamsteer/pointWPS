"""
Process to vegetation cover fraction:

Morsdorf, F., E. Meier, B. Kötz, K. I. Itten, M. Dobbertin & B. Allgöwer (2004) LIDAR-based geometric reconstruction of boreal type forest stands at single tree level for forest and wildland fire management. Remote Sensing of Environment, 92, 353-362.


"""

__author__ = 'Adam Steer'

#pywps parts
from pywps import Process, LiteralInput, ComplexInput, ComplexOutput, Format, FORMATS
from pywps.validator.mode import MODE
import logging

#python standard libraries
import os
import subprocess
import json
import re

#other python libraries
import pyproj

#from the python pointwps module:
from pointwps import metadata_query
from pointwps import wkt_transform

LOGGER = logging.getLogger("PYWPS")

class vegetationCoverFraction(Process):
    def __init__(self):
        inputs = [
            LiteralInput('polygon', 'WKT clipping polygon',
                        abstract='A WKT polygon defining the region of interest',
                          data_type='string'),
            LiteralInput('srid', 'WKT CRS (EPSG ID)',
                         abstract='The CRS of the WKT polygon - use the numeric part of an EPSG ID, eg 4326 for EPSG:4326. Default is 4326',
                         data_type='string',
                         default='4326'
                         ),
            LiteralInput('data_srid', 'WKT CRS (EPSG ID)',
                         abstract='The CRS of the underlying data - use the numeric part of an EPSG ID, eg 28355 for EPSG:28355',
                         data_type='string',
                         ),
            LiteralInput('gridcellsize', 'Grid cell size',
                          abstract='In addition to a single value per ROI, this process returns a rasterised cover fraction in each grid cell, delivered as a GeoTIFF. Caution - very small grid cells are likely meaningless unless your data are very dense. Default size is 25m',
                          data_type='float',
                          default=25.0),
            LiteralInput('dataset', 'Dataset/survey name (if known)',
                          data_type='string'),
                          allowed_values=['laz','pgsql','ply'],
                          data_type='string')
            ]
        outputs = [
            ComplexOutput('vcf_grid', 'Gridded vegetation cover fraction',
                           as_reference=True,
                           supported_formats=[Format('application/octet-stream')]),
            LiteralOutput('vcf', 'Gridded vegetation cover fraction')
            ]
        super(vegetationCoverFraction, self).__init__(
            self._handler,
            identifier='vegetation_coverfraction',
            version='0.1',
            title="Return vegetation cover fraction within region of interest",
            abstract='Provide a WKT polygon, a dataset name (* for any data in the region), and gridding cell size in metres. This process will return a per-ROI esimate of vegetation cover fraction (VCF) and a GeoTIFF with VCF per grid cell. Processing from Morsdorf, F., E. Meier, B. Kötz, K. I. Itten, M. Dobbertin & B. Allgöwer (2004) LIDAR-based geometric reconstruction of boreal type forest stands at single tree level for forest and wildland fire management. Remote Sensing of Environment, 92, 353-362.',
            profile='',
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True
            )

    def _handler(self, request, response):

        input_polygon = request.inputs['polygon'][0].data
        input_srid = request.inputs['srid'][0].data
        input_datasrid = request.inputs['data_srid'][0].data
        input_dataset = request.inputs['dataset'][0].data
        input_gridcellsize = request.inputs['gridcellsize'][0].data

        print input_polygon
        print input_pointfilter

        thefiles=metadata_query.query_metadata(input_polygon, input_srid, 'yes')

        print thefiles
        #from this we need a space-separated list of files
        files_parsed = json.loads(thefiles)

        #remove MKP files
        input_files=[]
        file_inds = [file.find('MKP') for file in files_parsed['files']]
        for i, item in enumerate(file_inds):
            if item < 0:
                input_files.append(files_parsed['files'][i])

        input_filelist = ' '.join(input_files)
        print input_filelist

        #transform the polygon to data srid (how do we know data srid?):
        clip_polygon = wkt_transform.transformwkt(input_polygon, input_srid, input_datasrid)
        print 'clipping polygon:'
        print clip_polygon

        # clip data from tiles
        # we want number of first returns and number of points with only one return

        # these points need to be ingested into a numpy array - maybe...

        # unless we can ferry dimensions, ie height to return #

        # but we need to know return # AND # returns, ie 1/1, 1/6 etc

        # something like:
        # firstreturns = data[ np.where(data['returnID'] == 1)]
        # singlereturns = data[ np.where(data['nreturns'] == 1)]

        # then:

        # VCF = (len(firstreturns) - len(singlereturns) / len(firstreturns)
        # for N metre grid cells?
        # make two grids
        # - ferry return # to elev, create count raster at N m
        # - ferry nreturns to elev, create raster at N m
        # difference rasters and divide by return raster -result is a VCF raster?

        ###or! grid in python...
        #hmmm.





        print "calling the tile clipping handler script"
        subprocess.call(['/local/pointwps/workerscripts/tilehandler.sh',
                        str(self.workdir),
                        input_filelist,
                        str(clip_polygon)
                        ])

        vcf =
        outfile = self.workdir + '/' + outfilename

        response.outputs['points'].file = outfile

        return response
