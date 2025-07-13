#!/bin/bash

set -x

mkdir /home/util

wget -P /home/util/libtorch https://download.pytorch.org/libtorch/cpu/libtorch-cxx11-abi-shared-with-deps-2.7.0%2Bcpu.zip

ls /home/util/libtorch

cd /home/util/libtorch && ls -A | grep libtorch | xargs unzip 

sleep 2

if [ -z "$( ls -A 'libtorch' )" ]; then
	echo "EMPTY"
	exit 1
else
	echo "NOT EMPTY"
	export LIBTORCH=/libtorch
fi


