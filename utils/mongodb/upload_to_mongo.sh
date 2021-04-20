#!/bin/bash
#
# SPDX-License-Identifier: Apache-2.0
# Copyright 2021, Intel Corporation

uploader_path=$(dirname ${BASH_SOURCE[0]})
json_files=$(find results -iname "result.json")

for f in ${json_files}; do
	${uploader_path}/upload_to_mongo.py ${f}
done
