__author__ = 'Adam Steer'

from pywps import Process, LiteralInput, ComplexInput, ComplexOutput, Format, FORMATS
from pywps.validator.mode import MODE

import os
import subprocess
import pdal
from osgeo import ogr

import logging
LOGGER = logging.getLogger("PYWPS")

class pointClipGDALDEM(Process):
    def __init__(self):
        inputs = [
            LiteralInput('polygon', 'WKT clipping polygon', 
                          data_type='string'),
            LiteralInput('dataset', 'Dataset/survey name (if known)',
                          data_type='string'),
            LiteralInput('tile_list', 'List of tiles',
                         abstract='Space delimited list of tiles to query. This input is temporary, or may not be required in future versions. Ideally input here is not manually generated',
                          data_type='string'),
            LiteralInput('resolution', 'DTM resolution in integer metres',
                          abstract='Desired DTM resolution (m). Please check point density first - and ensure your DTM setting reflect more than a single point per cell',
                          data_type='integer'),
            LiteralInput('radius', 'Search radius in metres.',
                        abstract='This value determines how many data points around a given cell should be used to compute a cell value. Enter 0 to use the default value of (1.5 x resolution)',
                        data_type='float'),
        
###we should really pass a JSON dictionary here, so complex input describing all the desired gdaldem options: http://www.gdal.org/gdaldem.html
                        
            ComplexInput('gdaldem_product', 'GDAL DEM products',
                          abstract='Which gdal_dem product do you want?',
                          data_type='json')
            ]
        outputs = [
            ComplexOutput('DTM', 'output clipped DTM',supported_formats=[Format('GEOTIFF')])
            ]
        super(pointClipDTM, self).__init__(
            self._handler,
            identifier='pointclipdtm',
            version='0.2',
            title="Return a GeoTIFF DTM from inside a WKT polygon",
            abstract='Provide a WKT polygon, a dataset name (* for any data in the region) - to return a rasterised DTM (using ground classified points). Currently restricted to a single dataset (ACT) - polygons outside of the data will return null. Output is currently limited to compressed LAZ format',
            profile='',
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True
            )

    def _handler(self, request, response):
        
        input_poly = request.inputs['poly'][0].data
        input_filelist = request.inputs['tile_list'][0].data
        input_resolution=request.inputs['resolution'][0].data
        input_radius = request.inputs['radius'][0].data
        input_cellvalue = request.inputs['cell_value'][0].data
        input_dataset = request.inputs['dataset'][0].data
        input_outtype = request.inputs['out_layers'][0].data
        
        #later - we will use Sean's DB
        #use a PostGIS store to get our file names
        #pg_connection = "dbname=tile_index user=pcbm password=pointy_cloudy host=127.0.0.1"
        #conn = ppg.connect(pg_connection)
        #cursor = conn.cursor()
        #blocks_query = "SELECT location WHERE st_intersects(GEOMETRY::st_geomfromtext($(input_poly))
        #'2154'))) FROM tiles;"
        #files = pdsql.read_sql(files_query, conn)
        print self.workdir
        
        print "radius: " + str(input_radius)
        print "resolution: " + str(input_resolution)
        
# we can try to do this in python - *if* we can parallelify the tile processing
# parts
        print "calling the handler script"
        subprocess.call(['/local/pywps/processes/tilehandler_dtm.sh',
                        str(self.workdir),
                        str(self.workdir),
                        "TIF",
                        input_dataset,
                        input_filelist,
                        str(input_poly),
                        str(input_resolution),
                        str(input_radius),
                        str(input_outtype)
                        ])

        outfile = self.workdir + '/' + input_dataset + '_clipped_dtm.tif'
        
        response.outputs['DTM'].file = outfile

        return response
