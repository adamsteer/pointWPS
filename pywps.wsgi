#!/usr/bin/python

activate_this = '/local/pointwps/pywps-venv/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

import os
import sys
import logging

logging.basicConfig(stream=sys.stderr)

os.environ['PYTHON_EGG_CACHE'] = '/local/pointwps/python-eggs'

sys.path.append("/local")
sys.path.append("/local/pointwps")
sys.path.append("/local/pointwps/processes")
sys.path.append("/local/pointwps/logs")

import pywps

from pywps.app.Service import Service

# processes need to be installed in PYTHON_PATH
#from processes.sayhello import SayHello
from processes.polygon_query import polygonQuery
from processes.tile2dtm import tile2dtm
#from processes.tile2raster import tile2raster
from processes.pointclip import pointClip
from processes.pointclipnormalised import pointClipNormalised
from processes.pointclipdtm import pointClipDTM
from processes.dartsample import dartSample

processes = [
  polygonQuery(),
  tile2dtm(),
  pointClip(),
  pointClipNormalised(),
  pointClipDTM(),
  dartSample()
  ]

# Service accepts two parameters:
# 1 - list of process instances
# 2 - list of configuration files
application = Service(
    processes,
    ['/local/pointwps/pywps.cfg']
)
