"""
Process to retrieve datasets and metadata which are contained in or intersected by a user-submitted WKT polygon.

Possible enhancements:
- implement a temporal filter
"""

__author__ = 'Adam Steer'

#pywps parts
from pywps import Process, LiteralInput, LiteralOutput
from pywps.validator.mode import MODE
import logging
LOGGER = logging.getLogger("PYWPS")

#python standard libraries
import os
import json
import requests
from collections import defaultdict

#from the python pointwps module:
from pointwps import metadata_query
from pointwps import path_transform


class polygonQuery(Process):
    def __init__(self):
        inputs = [
            LiteralInput('polygon', 'WKT search polygon',
                         abstract='WKT',
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
            LiteralInput('project', 'project ID',
                         abstract='data storage project',
                         data_type='string',
                         default='all',
                         min_occurs=0
                         ),
            LiteralInput('metadata', 'metadata response (or not)',
                         abstract='A switch to determine what metadata to return, if any. Default is none (file list only). For all available metadata use "all". Otherwise Provide a comma delimited list of words, options are: "density" (approximate point density of files intersecting ROI) , "count" (# of points in each file), "schema" (data storage schema equivalent to pdal info --schema), "classes" (approximate number of points in each class), "exactboundary" (exact boundary of point data as WKT multipolygon in native data CRS)',
                         data_type='string',
                         default='no',
                         min_occurs=0
                         )
            ]
        outputs = [
            LiteralOutput('metadata_response', 'Response metadata',
                         abstract='JSON dictionary of metadata which exist in the user-submitted polygon. Will be empty if no data exist in the ROI',
                         data_type='string')
            ]
        super(polygonQuery, self).__init__(
            self._handler,
            identifier='polygonquery',
            version='0',
            title="Query data with a WKT polygon",
            abstract='Provide a WKT polygon, and return a list of files which contain data inside the polygon. This process does not transform input polygons, it requires a user-defined SRS string which matches the coordinate system used in the polygon.',
            profile='',
            inputs=inputs,
            outputs=outputs,
            )

    def _handler(self, request, response):

        input_polygon = request.inputs['polygon'][0].data
        input_srid = request.inputs['srid'][0].data

        nodatamessage = str('No data were found in your polygon. Please check the input and data SRID, incorrect CRS definitions cause most data discovery issues.')

        if 'metadata' in request.inputs:
            input_metaswitch = request.inputs['metadata'][0].data
        else:
            input_metaswitch = 'none'
        if 'project' in request.inputs:
            input_project = request.inputs['project'][0].data
        else:
            input_project = 'all'

        print input_metaswitch

        if 'none' in input_metaswitch:
            metadata_return=metadata_query.query_metadata(input_polygon, input_srid, input_metaswitch, input_project)

            if metadata_return:
                metajson = json.loads(metadata_return)

                for counter, value in enumerate(metajson['files']):
                    metajson['files'][counter] = path_transform.remap_path(value)
                response.outputs['metadata_response'].data = metajson
                return response
            #if no files, return a sane message
            else:
                raise Exception(nodatamessage)

        elif 'all' in input_metaswitch :
            #all the metadata!
            metadata_return=metadata_query.query_metadata(input_polygon, input_srid, input_metaswitch, input_project)

            if metdata_return:
            #strip paths from files, and from filenames in the big JSON blob
                metajson = json.loads(metadata_return)
                #print metajson
            #basename files in files array
                for counter, value in enumerate(metajson['files']):
                    value = path_transform.remap_path(value)
                    metajson['files'][counter] = value
                    metajson['pdal'][counter]['filename'] = value

                response.outputs['metadata_response'].data = metajson
                return response

            else:
                raise Exception(nodatamessage)

        else:
            metadata_return=metadata_query.query_metadata(input_polygon, input_srid, 'all', input_project)
            if metadata_return:

                metadata_return_parsed = json.loads(metadata_return)

                metadict = defaultdict(dict)

                for counter, value in enumerate(metadata_return_parsed['files']):
                    value = path_transform.remap_path(value)
                    metadata_return_parsed['files'][counter] = value
                    metadata_return_parsed['pdal'][counter]['filename'] = value

                    if 'count' in input_metaswitch:
                        metadict[value]['point_count'] = metadata_return_parsed['pdal'][counter]['stats']['statistic'][0]['count']

                    if 'classes' in input_metaswitch:
                        metadict[value]['classes'] = metadata_return_parsed['pdal'][counter]['stats']['statistic'][0]['counts']

                    if 'density'in input_metaswitch:
                        metadict[value]['density'] = metadata_return_parsed['pdal'][counter]['boundary']['density']

                    if 'schema' in input_metaswitch:
                        metadict[value]['schema'] = metadata_return_parsed['pdal'][counter]['schema']

                    if 'exactboundary' in input_metaswitch:
                        metadict[value]['exactboundary'] = metadata_return_parsed['pdal'][counter]['boundary']['boundary']


                metajson = json.dumps(metadict)
                response.outputs['metadata_response'].data = metajson

                return response
            else:
                raise Exception(nodatamessage)
