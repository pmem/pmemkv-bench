#!/bin/bash
#
# SPDX-License-Identifier: Apache-2.0
# Copyright 2020-2021, Intel Corporation

edp_config_path=$(dirname ${BASH_SOURCE[0]})/edp_config.txt
pushd ${PMEMKV_BENCH_RESULTS_PATH} 
emon_files=$(find -iname "emon.dat")
for f in ${emon_files}; do
	pushd $(dirname ${f})
	emon -process-edp ${edp_config_path} 		
	popd
done
popd
