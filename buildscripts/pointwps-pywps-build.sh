#!/bin/bash
#Build Skua/WSGI

yum install -y \
python-pip \
python-virtualenv \
numpy \


#create a virtualenv
virtualenv -p /usr/bin/python /local/pointwps/pywps-venv

source /local/pointwps/pywps-venv/bin/activate

#update pip
pip install --upgrade pip

pip install setuptools packaging

pip install numpy

pip install cython

pip install requests pywps

pip install gdal==1.11.2 --global-option=build_ext --global-option="-I/usr/include/gdal"

pip install pdal

pip install pyproj

pip install shapely

pip install laspy

deactivate

##
