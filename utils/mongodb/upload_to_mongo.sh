#!/bin/bash
#
# SPDX-License-Identifier: Apache-2.0
# Copyright 2020-2021, Intel Corporation

json_files=$(find results -iname "result.json")
for f in ${json_files}; do
	cat ${f} | sed -e 's/"emon": 1/"emon": "1"/g' | sed -e 's/"emon": 0/"emon": "0"/g' | sed -e 's/"pmemkv_bench": {/"params": {/g' > ${f}_parsed.json
	/root/workspace/pmemkv-bench/upload_to_mongo.py ${f}_parsed.json
done
