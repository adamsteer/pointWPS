"""
Process to return points from data contained in a user-submitted WKT polygon. Can be filtered by class or range or any PDAL dimension (use polygon_query to explore available dimensions), but returns points essentially as-stored.

"""

__author__ = 'Adam Steer'

#pywps parts
from pywps import Process, LiteralInput, ComplexOutput, LiteralOutput, Format, FORMATS
from pywps.validator.mode import MODE
import logging

#python standard libraries
import os
import subprocess
import json
from datetime import datetime

#geospatial bits
from osgeo import ogr
import pdal

#from the python pointwps module:
from pointwps import nci_mas_query
from pointwps import wkt_transform

#global things
LOGGER = logging.getLogger("PYWPS")

class pointClip(Process):
    def __init__(self):
        inputs = [
            LiteralInput('polygon', 'WKT clipping polygon', 
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
                         
            LiteralInput('pointfilter', 'Point filter',
                         abstract='A PDAL-style range filter. See: https://www.pdal.io/stages/filters.range.html. For example, to return only buildings use [6:6], or only trees would be [4:5] (medium and high vegetation). You can filter on any other dimensions - use the metadata query process to discover the structure of your data', 
                         data_type='string',
                         min_occurs=0
                         ),
                         
            LiteralInput('output_format', 'Select an output format',
                         abstract='Output format: LAS, potree',
                         allowed_values=['las','potree'],
                         default='las',
                         data_type='string',
                         min_occurs=0
                         ),
            LiteralInput('outfilename', 'filename for the result of this process',
                         abstract='Output file name, no extension',
                         data_type='string',
                         min_occurs=0
                         )
            ]
        outputs = [
            ComplexOutput('points', 'output clipped point set',
                           as_reference=True,
                           supported_formats=[Format('application/octet-stream')])
            ]
        super(pointClip, self).__init__(
            self._handler,
            identifier='pointclip',
            version='0.4',
            title="Return LiDAR points from inside a WKT polygon",
            abstract='Provide a WKT polygon, a dataset name (* for any data in the region), and a classification filter in PDAL format (see documentation for filters.range) - to return a point dataset within the polygon as either compressed LAS (1.2) or a Potree package',
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
        
        #handling optional inputs...
        #defaults to 'use all datasets in my polygon'
        if 'dataset' in request.inputs:
            input_dataset = request.inputs['dataset'][0].data
        else:
            input_dataset = 'all'
        
        if 'outfilename' in request.inputs:
            input_outfilename = request.inputs['outfilename'][0].data
        else:
            input_outfilename = 'points_'+input_datasrid
        
        if 'pointfilter' in request.inputs:
            input_pointfilter = request.inputs['pointfilter'][0].data
        else:
            input_pointfilter = 'Classification[0:18]'

        if 'output_format' in request.inputs:
            input_writeformat = request.inputs['output_format'][0].data
        else:
            input_writeformat = 'las'
            
            
        print input_polygon
        print input_pointfilter
        print input_writeformat
        
        nodatamessage = str('No data were found in your polygon. Please check the input and data SRID, incorrect CRS definitions cause most data discovery issues.')
        
        #intersect only for now... and don't restrict datasets
        mas_return=nci_mas_query.query_mas(input_polygon, input_srid, 'yes')
        
        #fail quickly - return a nodata message asap.
        if mas_return:

            input_filelist=nci_mas_query.remove_unclassified(mas_return)
            
            #transform the polygon to data srid (how do we know data srid? for now
            # we provide it as an input):
            clip_polygon = wkt_transform.transformwkt(input_polygon, input_srid, input_datasrid)
            print 'clipping polygon:'
            print clip_polygon

            outfilename = input_outfilename + '_clipped'

            print outfilename
            print "calling the tile clipping handler script"
            subprocess.call(['/local/pointwps/workerscripts/tilehandler.sh',
                            str(self.workdir),
                            input_filelist,
                            str(clip_polygon)
                            ])
                            
            # generate potree output. Experimental!!!!
            if 'potree' in input_writeformat:
                print "calling the patch merging script"
                subprocess.call(['/local/pointwps/workerscripts/to_potree.sh',
                                str(self.workdir),
                                str(outfilename)
                                ])
                outfile = self.workdir + '/' + outfilename + '_potree.zip'
                response.outputs['points'].file = outfile
                
            if 'las' in input_writeformat:
                print "calling the patch merging script"
                
                outfilename = outfilename + '.las'
                
                subprocess.call(['/local/pointwps/workerscripts/merge_points.sh',
                                str(self.workdir),
                                str(input_writeformat),
                                str(input_pointfilter),
                                str(outfilename)
                                ])
                outfile = self.workdir + '/' + outfilename
                response.outputs['points'].file = outfile
            
            return response
        else:
            raise Exception(nodatamessage)