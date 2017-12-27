"""
Process to return a rasterised digital terrain model from data contained in a user-submitted WKT polygon.

Possible enhancements:
- void filling the resulting DTM
- avoiding writing temporary data to disk

What GDAL output formats should we support?
http://www.gdal.org/formats_list.html

"""

__author__ = 'Adam Steer'

#pywps parts
from pywps import Process, LiteralInput, LiteralOutput, ComplexInput, ComplexOutput, Format, FORMATS, exceptions
from pywps.validator.mode import MODE
import logging

#python standard libraries
import os
import subprocess
import json

#from the python pointwps module:
from pointwps import metadata_query
from pointwps import wkt_transform

#global things
LOGGER = logging.getLogger("PYWPS")

class pointClipDTM(Process):
    def __init__(self):
        inputs = [
            LiteralInput('polygon', 'WKT clipping polygon',
                          abstract='A WKT polygon defining the region of interest. Points inside the polygon will be used to create a DTM',
                          data_type='string'
                          ),
            LiteralInput('srid', 'WKT CRS (EPSG ID)',
                         abstract='The CRS of the WKT polygon - use the numeric part of an EPSG ID, eg 4326 for EPSG:4326. Default is 4326',
                         data_type='string',
                         default='4326'
                         ),
            LiteralInput('data_srid', 'WKT CRS (EPSG ID)',
                         abstract='The CRS of the underlying data - use the numeric part of an EPSG ID, eg 28355 for EPSG:28355',
                         data_type='string',
                         ),
            LiteralInput('dataset', 'Dataset/survey name (if known)',
                          abstract='Restrict results to a specific survey or data catalogue - not yet implemented, default is all possible.',
                          data_type='string',
                          default='all',
                          min_occurs=0
                          ),
            LiteralInput('resolution', 'DTM resolution in metres',
                          abstract='Desired DTM resolution (m). Please check point density first and ensure your DTM settings reflect more than a single point per cell. Default is 5 m.',
                          data_type='float',
                          min_occurs=0
                          ),
            LiteralInput('radius', 'Optional search radius scale in metres.',
                          abstract='This value determines how many data points around a given cell should be used to compute a cell value. Default value is 1.5 x resolution, leave input out if the default value is fine.',
                          data_type='float',
                          min_occurs=0
                          ),
            LiteralInput('gdal_driver', 'Optional GDAL output driver',
                          abstract='Optionally define which GDAL format to use, default and current only option is GTiff',
                          data_type='string',
                          default='GTiff',
                          min_occurs=0
                          ),
            LiteralInput('out_layers', 'Optional DTM type and stats outputs',
                          abstract='A comma separated list of one or more possible cell values: mean, min, max, idw, stdev, count, all. Default is "mean" - which will be used if this input is omitted. To control your outpur results, create a comma separated list of one or more output types. The results will be stacked into bands, in order of appearance in the list. For example using "all" will create a 6-band raster with all outputs. Using "mean" will create a single band raster populated with mean cell heights. Using "count" will create a proxy for point density, a single band raster populated with cell counts. See the PDAL writers.gdal documentation for more: https://www.pdal.io/stages/writers.gdal.html',
                          data_type='string',
                          default='mean',
                          min_occurs=0
                          )
            ]
#        outputs = [
#            ComplexOutput('DTM', 'output clipped #DTM',supported_formats=[Format('GEOTIFF')])
#            ]
        outputs = [
            ComplexOutput('DTM', 'output DTM',
                           abstract="raster DTM (ground points) from input LAS/LAZ tile",
                           supported_formats=[Format('image/tiff; subtype=geotiff')],
                           as_reference=True)
            ]

        super(pointClipDTM, self).__init__(
            self._handler,
            identifier='pointclipdtm',
            version='0.4',
            title="Return a GeoTIFF DTM from inside a WKT polygon",
            abstract='Provide a WKT polygon, a dataset name (* for any data in the region) - to return a rasterised DTM (using ground classified points).',
            profile='',
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True
            )

    def _handler(self, request, response):

        #required inputs
        input_polygon = request.inputs['polygon'][0].data
        input_srid = request.inputs['srid'][0].data
        input_datasrid = request.inputs['data_srid'][0].data

        #handling optional inputs...
        #defaults to 'use all datasets in my polygon'
        if 'dataset' in request.inputs:
            input_dataset = request.inputs['dataset'][0].data
        else:
            input_dataset = 'all'
        #default grid cell size is 5m
        if 'resolution' in request.inputs:
            input_resolution=request.inputs['resolution'][0].data
        else:
            input_resolution = 5
        #default radius of points used for cell is 1.5* cell size
        if 'radius' in request.inputs:
            input_radius = request.inputs['radius'][0].data
        else:
            input_radius = 1.5 * input_resolution
        #default output is geotiff
        if 'gdal_driver' in request.inputs:
            input_gdaldriver = request.inputs['gdal_driver'][0].data
        else:
            input_gdaldriver = r'GTiff'
        #default is 'make DTM cells equal mean cell value'
        if 'out_layers' in request.inputs:
            input_outlayers = request.inputs['out_layers'][0].data
        else:
            input_outlayers = r'mean'

        nodatamessage = str('No data were found in your polygon. Please check the input and data SRID, incorrect CRS definitions cause most data discovery issues.')

        #use the metadata system to collect files we need to work on
        #to do: implement dataset selection - for example if the query
        # picks data from mutliple overlapping surveys, which do we use?
        # DON'T transform the polygon to data srid here, the metadata system
        # should know what to do
        print input_polygon

        #we only want files...
        metadata_return=metadata_query.query_metadata(input_polygon, input_srid)

        #fail quickly - return a nodata message asap.
        if metadata_return:
            input_filelist=nci_metadata_query.remove_unclassified(metadata_return)

            #transform the polygon to data srid (how do we know data srid? for now
            # we provide it as an input):
            clip_polygon = wkt_transform.transformwkt(input_polygon, input_srid, input_datasrid)
            print 'clipping polygon:'
            print clip_polygon

            #this really needs to reflect the GDAL driver.. hmm.
            outfilename = input_dataset + '_clipped_dtm.tif'

            print outfilename
            print "radius: " + str(input_radius)
            print "resolution: " + str(input_resolution)

            print "calling the tile clipping handler script"
            subprocess.call(['/local/pointwps/workerscripts/tilehandler.sh',
                            str(self.workdir),
                            input_filelist,
                            str(clip_polygon)
                            ])

            print "calling the patch merging and rasterisation script"
            subprocess.call(['/local/pointwps/workerscripts/merge_dtm.sh',
                            str(self.workdir),
                            str(input_resolution),
                            str(input_radius),
                            str(input_outlayers),
                            str(input_gdaldriver),
                            str(outfilename)
                            ])

            outfile = self.workdir + '/' + outfilename
            response.outputs['DTM'].file = outfile
            return response
        else:
            raise Exception(nodatamessage)
