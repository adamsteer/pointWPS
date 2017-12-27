__author__ = 'Adam Steer'

from pywps import Process, LiteralInput, ComplexInput, ComplexOutput, Format, FORMATS
from pywps.validator.complexvalidator import validategeojson

from pywps.validator.mode import MODE

import os
import tempfile
import pdal
from osgeo import ogr
import gdal
import subprocess


class pointdensity(Process):
    def __init__(self):
        inputs = [
            LiteralInput('dataset','Path to LAS tile',
                         abstract="provide a LAS/LAZ format tile path",
                         data_type='string'),
            ]
        outputs = [
            LiteralOutput('density', 'dataset density',
                           abstract="Point density estimate for requested dataset",
                           data_type='string'),
            ]

        super(pointdensity, self).__init__(
            self._handler,
            identifier='pointdensity',
            version='0.1',
            title="Return a point density estimate from the input tile set",
            abstract='Return a point density estimate from input data. Currently restricted to a single dataset (ACT) - polygons outside of the data will return null',
            profile='',
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True,
            )

    def _handler(self, request, response):
        #what do we want to do here - long density or short density?
        # in the long term we do this from a metadata store query...

        input_dataset = request.inputs['dataset'][0].data

        pipe_params = list([input_tile,input_resolution,radius])
        ##sample... https://github.com/PDAL/PDAL/pull/1367#issuecomment-259834948
        json = """
            {
            "pipeline": [
             "%(thefiles)s",
            {
              "type": "filters.range",
              "limits": "Classification[2:2]"
            },
            {
              "type": "writers.gdal",
              "resolution": %(the_res)s,
              "radius": %(the_rad)s,
              "gdaldriver": "GTiff",
              "filename": "output.tif",
              "output_type": "mean"
              }
              ]
            }""" % {'thefiles': input_tile, 'the_res': input_resolution, 'the_rad': radius}

        subprocess.call(['pdal',
                        'pipeline',
                        jsonfile,
                        ])

        print json

        pipeline = pdal.Pipeline(unicode(json))
        count = pipeline.execute()
        #arrays = pipeline.arrays
        #metadata = r.metadata
        #log = pipeline.log


        #dtm = gdal.Open(dtmfile)
        #dtmdata = dtm.GetRasterBand(1)
        #metadata = dtmdata.GetMetadata()

        #print metadata


        response.outputs['density'].data = thedensity
        response.outputs['DTM'].file = dtmfile

        return response
