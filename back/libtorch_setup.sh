#!/bin/bash

set -x

wget -q -P /home/$USER/libtorch https://download.pytorch.org/libtorch/cpu/libtorch-cxx11-abi-shared-with-deps-2.7.0%2Bcpu.zip

cd ~/home/$USER/libtorch && ls -A | grep libtorch | xargs unzip 

sleep 2

if [ -z "$( ls -A 'libtorch' )" ]; then
	echo "EMPTY"
	exit 1
else
	echo "NOT EMPTY"
	export LIBTORCH=/home/$USER/libtorch/libtorch
fi


