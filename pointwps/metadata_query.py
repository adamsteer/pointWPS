"""
Code for querying a metadata storage system

Adam Steer
July 2017

Input is:
- a string WKT polygon
- an integer SRS number (numerical part of an EPSG code), which gives the
  coordinate system of the WKT string
- a string boolean switch for metadata ('yes' or 'no'). 'yes' returns a list of files
  and their complete metadata. 'no' (default) returns only a list of files

Output is:
- a list of files whos spatial extents intersect (or are contained by) the WKT polygon
- optionally all metadata associated with each file
- optionally a list of all files which do not have 'MKP' or 'unclassified' in their path

This all might work better to return an object which has a set of results/methods, and a query URL.

***CAUTION***

This module was built for a bespoke metadata store used internally at the National Computational Infrastructure
(http://nci.org.au). It is not tested with a generic metadata store yet.

TO DO:

- create a metadata storage schema
- implement and test pointWPS with the new storage schema

In general, the storage schema requires postGIS, a geometry defining data bounding boxes,
and a path to a resource on a file system or object store.

"""
import json
import requests

MGA_SRID_MAP = {
             "z50":"28350",
             "z51":"28351",
             "z52":"28352",
             "z53":"28353",
             "z54":"28354",
             "z55":"28355",
             "z56":"28356"
             }

def construct_request(wkt, srs, metadata, project):
    """
    Ingest a WKT polygon string, it's numerical SRID code and a metadata 'yes/no'
    switch, and returns a result from a metadata system.
    Input:
    - string WKT polygon
    - integer SRID code
    - 'all' or 'none' to obtain full metadata records for each matching file or not.
    - project ID if known
    """

    #this provides mapping between a project key and a file path
    project_map={
                "project_key":"/path/to/project/root"
                }

    #intersect only for now... and don't restrict datasets
    # assumes database is exposed via a web API, not a direct DB call
    API_urlroot = "..."
    if project == 'all':
        API_urlroot = API_urlroot+"/g"
    else:
        API_urlroot = API_urlroot+project_map[project]

    API_request= "intersects"
    API_srid = "EPSG:"+srs
    API_wkt = wkt.replace(" ","+")
    if metadata != 'none':
        request_url = API_urlroot+"?"+API_request+"&srs="+API_srid+"&wkt="+API_wkt+"&metadata=pdal"
    else: # there can be no other case which would return metadata right now..
        request_url = API_urlroot+"?"+API_request+"&srs="+API_srid+"&wkt="+API_wkt

    return request_url

def remove_unclassified(mas_return):
    """
    Parse the JSON document returned by MAS and return only classified tiles using a
    filename reading approach - for example any files witn 'MKP' or 'unclassified'
    in the file name are removed from the file list to send for further processing.

    inputs: A MAS query response (JSON)
    outputs: A space delimited string of file paths
    """
    #parse MAS JSON
    mas_return_parsed = json.loads(mas_return)

    #remove MKP and unclassified files - clunky but works!
    filtered_files = [file for file in mas_return_parsed['files'] if ('MKP' not in file) if ('mkp' not in file) if ('unclassified' not in file) if ('Unclassified' not in file)]

    #turn list into a string with space separators
    input_filelist = ' '.join(filtered_files)

    #return the string
    return input_filelist


def query_metadata(wkt, srs, metadata='none',project='all'):
    """
    Really simple: sends a query constructed by construct_request, parses the result
    to an ASCII string.
    """
    request_url = construct_request(wkt, srs, metadata, project)
    result=requests.get(request_url)

    #here we decode the JSON

    json_metadata = result.content.decode('ascii')

    metajson = json.loads(json_metadata)
    if len(metajson['files']) > 0:
        return json_metadata
    else:
        return False

if __name__ == '__main__':
    main()
