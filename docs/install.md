# Installing pointWPS


## Assumptions:

- you have a CentOS virtual machine
- you have root permissions on the VM
- *you have already provisioned yourself a VM and logged in*
- apache 2.0 with a configured virtualhost for WSGI. You may need to edit this for the correct server address
- Postgres 9.6 and postGIS
- Postgres firewall set up ready

## 1. clone the pointWPS repository

head to `/local/`, give yourself sudo permissions and clone this repo. This gives you a folder named `/local/pointwps` (the repo name will change to pointwps soon). Now `cd pointwps`.

## 2. Set up PDAL

From `/local/pointwps`, type `sh ./buildscripts/pdal_depends.sh` (with sudo) and go grab a coffee or do some push ups. If no errors, then type `sh ./buildscripts/pdal_build.sh` (with sudo) and repeat. More pushups or more coffee.

The first script does a bunch of yum installs for the PDAL ecosystem's many dependencies. The second does a bunch of git pulls and builds for software not in the CentOS repo system.

## 3. Set up a python environment for pyWPS

If all went well in step 2, type `sh ./buildscripts/pointwps-pywps-build.sh`. This provisions a python virtual environment that PyWPS will use.

## 4. Move the cleanup script to the right spot

`cp ./buildscripts/pywps-results-clean /etc/cron.hourly/ && chmod a+rx /etc/cron.hourly/pywps-results-clean`

## 5. Create your working temp and output directories

(this might already be done in Puppet - check first!)

`cd /local/`

`mkdir -p pointwps/workdir && chown apache pointwps/workdir`

`mkdir -p pointwps/outputs && chown apache pointwps/outputs`

## 6. test!

At the terminal, tail the apache log: `tail -f /var/log/httpd/servername_error.log` and hit the URL: `http://servername/wps?service=wps&version=1.0.0&request=getcapabilities` in a browser.

All being well, the browser will spew a bunch of XML describing the WPS server, and apache will fail to show you any python errors. If you do see Python errors or permission errors, track them down! or log an issue!
