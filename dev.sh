#!/bin/sh

set -x

mkdir /server_data 
chown 755 -R /server_data


mkdir /metadata
chown 755 -R /metadata

cd /metadata
