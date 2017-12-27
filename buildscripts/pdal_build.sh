#!/bin/bash
#Build the PCVM
#taken heavily from here:
# https://github.com/PDAL/PDAL/tree/master/scripts/linux-install-scripts

#make the dir /local/build if it doesn't exist. not yet automated

buildroot="/local/build"
buildcores=4

echo "creating build directory if it doesn't exist"
[ -d $buildroot ] || mkdir -p $buildroot

echo "moving to $buildroot"
cd $buildroot
pwd
echo "======================================"

echo "installing jsoncpp"
#install jsoncpp from source:
if [ ! -d $buildroot/jsoncpp ]; then
    git clone https://github.com/open-source-parsers/jsoncpp.git
    git checkout tags/1.8.0
else
    cd $buildroot/jsoncpp
    git pull
fi
if [ ! -d $buildroot/jsoncpp-build ]; then
    mkdir $buildroot/jsoncpp-build
fi
cd $buildroot/jsoncpp-build
cmake3 $buildroot/jsoncpp -G "Unix Makefiles" \
                          -DCXX_FLAGS=fPIC \
                          -DCMAKE_INSTALL_PREFIX=/usr/local \
                          -DBUILD_SHARED_LIBS=ON \
                          -DBUILD_STATIC_LIBS=ON \
                          -DCMAKE_BUILD_TYPE=Release \
                          && make -j$buildcores && make install && make clean && ldconfig
cd $buildroot
#installs into /usr/lib - note this for entwine build

#echo "building GDAL 2.2.1"
#GDAL
#if [ ! -d $buildroot/gdal-2.2.1 ]; then
#    wget http://download.osgeo.org/gdal/2.2.1/gdal-2.2.1.tar.gz#    tar -xvf gdal-2.2.1.tar.gz
#fi
#cd $buildroot/gdal-2.2.1
#./configure --prefix=/usr/ --with-python
#make -j$buildcores && make install && ldconfig && make clean

#check version in case anyone is watching...
#gdalinfo --version

cd $buildroot

echo "installing laz-perf"
#laz-perf
if [ ! -d $buildroot/laz-perf ]; then
    git clone https://github.com/hobu/laz-perf.git
else
    cd $buildroot/laz-perf
    git pull
fi
if [ ! -d $buildroot/lazperf-build ]; then
    mkdir $buildroot/lazperf-build
fi
cd $buildroot/lazperf-build
cmake3 $buildroot/laz-perf -G "Unix Makefiles" \
                          -DCMAKE_INSTALL_PREFIX=/usr \
                          -DCMAKE_BUILD_TYPE=Release \
                          && make -j$buildcores && make install && make clean && ldconfig
cd $buildroot

echo "installing laszip"
#laszip
#git clone https://github.com/LASzip/LASzip.git laszip
#download package, unzip and build. Build from git is breaking.
if [ ! -d $buildroot/LASzip ]; then
    git clone https://github.com/LASzip/LASzip.git
    cd $buildroot/LASzip
    #every other commit on LASzip comes with free compiler errors!
    # from here: https://github.com/connormanning/entwine/blob/master/scripts/ubuntu-deps.sh
    git checkout 6de83bc3f4abf6ca30fd07013ba76b06af0d2098
fi
if [ ! -d $buildroot/laszip-build ]; then
    mkdir $buildroot/laszip-build
fi
cd $buildroot/laszip-build
cmake3 $buildroot/LASzip -DCMAKE_INSTALL_PREFIX=/usr \
                                  -DCMAKE_BUILD_TYPE=Release \
                                  && make -j$buildcores && make install && make clean && ldconfig
cd $buildroot

echo "installing hexer"
#hexer

if [ ! -d $buildroot/hexer ]; then
    git clone https://github.com/hobu/hexer.git
else
    cd $buildroot/hexer
    git pull
fi
if [ ! -d $buildroot/hexer-build ]; then
    mkdir $buildroot/hexer-build
fi
cd $buildroot/hexer-build
cmake3 $buildroot/hexer -DCMAKE_INSTALL_PREFIX=/usr \
                       -DWITH_GDAL=ON \
                       -DCMAKE_BUILD_TYPE=Release \
                       && make -j$buildcores && make install && make clean && ldconfig
cd $buildroot

echo "installing libGHT"
#libGHT (for postgres-pointcloud)
if [ ! -d $buildroot/libght ]; then
    git clone https://github.com/pramsey/libght.git
else
    cd $buildroot/libght
    git pull
fi
if [ ! -d $buildroot/libght-build ]; then
    mkdir $buildroot/libght-build
fi
cd $buildroot/libght-build
cmake $buildroot/libght -DCMAKE_INSTALL_PREFIX=/usr \
                        -DCMAKE_BUILD_TYPE=Release \
                        && make -j$buildcores && make install && make clean && ldconfig
cd $buildroot

echo "installing postgres-pointcloud"
#pgpointcloud

if [ ! -d $buildroot/pointcloud ]; then
    git clone https://github.com/pramsey/pointcloud.git
else
    cd $buildroot/pointcloud
    git pull
fi
if [ ! -d $buildroot/pointcloud-build ]; then
    mkdir $buildroot/pointcloud-build
fi
cd $buildroot/pointcloud-build
cmake3 $buildroot/pointcloud -DPG_CONFIG="/usr/pgsql-9.6/bin/pg_config" \
                             -DCMAKE_BUILD_TYPE=Release \
                             && make -j$buildcores && make install && make clean && ldconfig
cd $buildroot

echo "installing PDAL"
#...and finally PDAL!
if [ ! -d $buildroot/PDAL ]; then
    git clone https://github.com/PDAL/PDAL.git
    #stick to a release - maybe
    git checkout tags/1.5.0
    cd $buildroot
else
    cd $buildroot/PDAL
    git checkout tags/1.5.0
    git pull
    cd $buildroot
fi
if [ ! -d $buildroot/PDAL-build ]; then
    mkdir $buildroot/PDAL-build
fi
cd $buildroot/PDAL-build
#laszip turned off, it can't handle LAS1.4
cmake3 $buildroot/PDAL \
               -DBUILD_PLUGIN_HEXBIN=ON \
               -DBUILD_PLUGIN_ICEBRIDGE=ON \
               -DBUILD_PLUGIN_PGPOINTCLOUD=ON \
               -DBUILD_PLUGIN_PYTHON=ON \
               -DBUILD_PLUGIN_SQLITE=ON \
               -DBUILD_SHARED_LIBS=ON \
               -DBUILD_SQLITE_TESTS=ON \
               -DBUILD_TESTING=ON \
               -DCMAKE_BUILD_TYPE=Release \
               -DWITH_COMPLETION=ON \
               -DWITH_LASZIP=ON \
               -DWITH_LAZPERF=ON \
               -DWITH-PYTHON=ON \
               -DCMAKE_INSTALL_PREFIX=/usr \
               -DGEOTIFF_INCLUDE_DIR=/usr/include/libgeotiff \
               -DJSONCPP_INCLUDE_DIR=/usr/local/include/jsoncpp \
               -DJSONCPP_LIBRARY=/usr/local/lib64/libjsoncpp.so \
               -DWITH_TESTS=ON \
               && make -j$buildcores && make install && make clean && ldconfig
cd $buildroot

echo "installing entwine"
#then entwine
if [ ! -d $buildroot/entwine ]; then
    git clone https://github.com/connormanning/entwine.git
    cd $buildroot/entwine
    git checkout tags/1.1.0
    cd $buildroot
else
    cd $buildroot/entwine
    git pull
    git checkout tags/1.1.0
    cd $buildroot
fi
if [ ! -d $buildroot/entwine-build ]; then
    mkdir $buildroot/entwine-build
fi
cd $buildroot/entwine-build
cmake3  $buildroot/entwine -G "Unix Makefiles" \
       -DCMAKE_INSTALL_PREFIX=/usr \
       -DCMAKE_BUILD_TYPE=Release \
       -DJSONCPP_LIBRARY=/usr/local/lib/libjsoncpp.so \
       -DJSONCPP_INCLUDE_DIR=/usr/local/include/jsoncpp \
       && make -j$buildcores && make install && make clean && ldconfig
cd $buildroot

echo "grabbing a Potree source"

if [ ! -d /local/potree ]; then
    cd /local/
    git clone https://github.com/potree/potree.git
else
    cd /local/potree
    git pull
fi

echo "installing PotreeConverter"

#need newer gcc
scl enable devtoolset-6 bash

#since Potree doesn't use system LASzip right now...
if [ ! -d $buildroot/ms_lastools ]; then
    git clone https://github.com/m-schuetz/LAStools.git ms_lastools
else
    cd $buildroot/ms_lastools
    git pull
fi
cd $buildroot/ms_lastools/LASzip/
mkdir build && cd build
cmake -DCMAKE_BUILD_TYPE=Release .. && make

cd $buildroot

#now install PotreeConverter

if [ ! -d $buildroot/PotreeConverter ]; then
    git clone https://github.com/potree/PotreeConverter.git
else
    cd $buildroot/PotreeConverter
    git pull
fi
if [ ! -d $buildroot/potreeconverter-build ]; then
    mkdir $buildroot/potreeconverter-build
fi
cd $buildroot/potreeconverter-build

cmake -DCMAKE_BUILD_TYPE=Release -DLASZIP_INCLUDE_DIRS=/local/build/ms_lastools/LASzip/dll -DLASZIP_LIBRARY=/local/build/ms_lastools/LASzip/build/src/liblaszip.so ../PotreeConverter

#pointWPS refers to Potreeconverter from /local/build/... so for now just make...
make

cd $buildroot
# exit devtoolset
exit




#all wrapped up!
echo "done"