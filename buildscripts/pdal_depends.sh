#!/bin/bash

#dependencies for PDAL
yum install -y \
boost \
boost-devel \
bzip2 \
bzip2-devel \
cmake3 \
cmake-gui \
CUnit-devel \
eigen3-devel \
expat-devel \
flann \
flann-devel \
gcc-c++ \
gdal \
gdal-devel \
geos \
geos-devel \
hdf5-devel \
jsoncpp \
jsoncpp-devel \
libarchive-devel \
libatomic \
libcurl-devel \
libgeotiff \
libgeotiff-devel \
libpqxx \
libpqxx-devel \
libtiff \
libtiff-devel \
libxml2-devel \
lzip \
ncurses-devel \
netcdf-devel \
numpy \
openjpeg \
openjpeg-devel \
proj \
proj-devel \
python-devel \
SFCGAL \
SFCGAL-devel \
sqlite \
sqlite-devel \
wget \
xz-devel \
centos-release-scl \
devtoolset-6

#postgres/postgis may or may not be provisioned by puppet
yum install -y \
https://yum.postgresql.org/9.6/redhat/rhel-7-x86_64/pgdg-centos96-9.6-3.noarch.rpm

yum install -y \
postgresql96-server \
postgresql96 \
postgresql96-devel \
postgresql96-contrib \
postgis \
postgis-utils \
