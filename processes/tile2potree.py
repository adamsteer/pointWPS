__author__ = 'Adam Steer'

#pywps parts
from pywps import Process, LiteralInput, ComplexInput, ComplexOutput, Format, FORMATS
from pywps.validator.mode import MODE
import logging

#python standard libraries
import os
import subprocess
import math

#geospatial bits
import pdal
from osgeo import ogr
import gdal

#from the python pointwps module:
from pointwps import path_transform

class tile2dtm(Process):
    def __init__(self):
        inputs = [
            LiteralInput('dataset','Path to LAS tile',
                         abstract="provide a LAS/LAZ format tile path",
                         data_type='string'),
            LiteralInput('resolution', 'DTM resolution in metres',
                          abstract='Desired DTM resolution (m). Please check point density first and ensure your DTM settings reflect more than a single point per cell. Default is 5 m.',
                          data_type='float',
                          default=5,
                          min_occurs=0
                          ),
            LiteralInput('radius', 'Optional search radius scale in metres.',
                          abstract='This value determines how many data points around a given cell should be used to compute a cell value. Default value is 1.5 x resolution, leave input out if the default value is fine.',
                          data_type='float',
                          default=7.5,
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
        outputs = [
            ComplexOutput('DTM', 'output DTM',
                           abstract="raster DTM (ground points) from input LAS/LAZ tile", 
                           supported_formats=[Format('application/octet-stream')], 
                           as_reference=True),
            ]
        super(tile2dtm, self).__init__(
            self._handler,
            identifier='tile2dtm',
            version='0.3',
            title="Return DTM from a given tile",
            abstract='Provide a tile name and a resolution (m) to return a GeoTIFF DTM.',
            profile='',
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True,
            )

    def _handler(self, request, response):

        #print request.inputs
        input_tile = path_transform.unmap_path(request.inputs['dataset'][0].data)
        
        
        #handling optional inputs...
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

        infile = os.path.basename(input_tile)
        outfilename = infile[:-4]
        
        print outfilename
        
        print self.workdir

        ##sample... https://github.com/PDAL/PDAL/pull/1367#issuecomment-259834948
        json = """
            {
            "pipeline": [
             "%(thefile)s",
            {
              "type": "filters.range",
              "limits": "Classification[2:2]"
            },
            {
              "type": "writers.gdal",
              "resolution": %(the_res)s,
              "radius": %(the_rad)s,
              "gdaldriver": "%(the_driver)s",
              "filename": "%(outfile)s",
              "output_type": "%(out_layers)s"
              }
              ]
            }""" % {'thefile': input_tile, 'the_res': input_resolution, 'the_rad': input_radius, 'the_driver': input_gdaldriver, 'outfile': outfilename, 'out_layers': input_outlayers }

        print json
        
        pipeline = pdal.Pipeline(unicode(json))
        count = pipeline.execute()
        #arrays = pipeline.arrays
        #metadata = r.metadata
        #log = pipeline.log
        
        dtmfile = self.workdir + '/' + outfilename
        
        print dtmfile

        #dtm = gdal.Open(dtmfile)
        #dtmdata = dtm.GetRasterBand(1)
        #metadata = dtmdata.GetMetadata()
        
        #print metadata

        response.outputs['DTM'].output_format = FORMATS.GEOTIFF
        response.outputs['DTM'].file = dtmfile
        #response.outputs['DTM'].metadata = unicode(metadata)
         
        return response
