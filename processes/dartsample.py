__author__ = 'Adam Steer'

from pywps import Process, LiteralInput, ComplexInput, ComplexOutput, Format, FORMATS
from pywps.validator.mode import MODE

import os
import subprocess
import pdal
#from osgeo import ogr

from pointwps import metadata_query

import logging
LOGGER = logging.getLogger("PYWPS")

class dartSample(Process):
    def __init__(self):
        inputs = [
            LiteralInput('poly', 'clipping polygon (WKT)',
                          data_type='string'),
            LiteralInput('distance', 'minimum separation of points (m)',
                          data_type='float'),
            LiteralInput('classfilter', 'Classification filter',
                          data_type='string'),
            LiteralInput('output_format', 'Select an output format',
                         abstract='Output format: LAZ (now), binary PLY',
                          allowed_values=['LAZ','PLY'],
                          data_type='string')
            ]
        outputs = [
            ComplexOutput('points', 'output clipped point set',
                           as_reference=True,
                           supported_formats=[Format('application/octet-stream')])
            ]
        super(dartSample, self).__init__(
            self._handler,
            identifier='dartsample',
            version='0.1',
            title="Poisson dart sampler for point density homogenisation",
            abstract='Provide a GeoJSON polygon, a dataset name (* for any data in the region), a point separation (m), and a classification filter (eg [2:2] for ground). Returns a point set clipped to the polygon and resampled at the minimum point spacing using a Poisson dart throwing method.',
            profile='',
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True
            )

    def _handler(self, request, response):

        input_poly = request.inputs['poly'][0].data
        input_distance = request.inputs['distance'][0].data
        input_classfilter = request.inputs['classfilter'][0].data
        input_writeformat = request.inputs['output_format'][0].data

        ##sample... https://github.com/PDAL/PDAL/pull/1367#issuecomment-259834948
        json = """
            {
            "pipeline": [
            %(thefiles)s
            {
              "type": "filters.crop",
              "polygon": "%(poly)s"
              },
              {
              "type":"filters.sample",
              "radius":"%(distance)"
             },
            {
              "type": "writers.las",
              "filename": "%(outpoints)s"
              }
              ]
            }"""  % {'thefiles': file_list, 'poly': input_poly, 'distance': input_distance, 'outpoints': self.workdir + '/sampledpoints.laz' }


        #pipeline = pdal.Pipeline(unicode(json))
        #count = pipeline.execute()
        #arrays = pipeline.arrays
        #metadata = r.metadata
        #log = pipeline.log

        outfile = self.workdir + '/sampledpoints.laz'

        response.outputs['points'].file = outfile

        return response
