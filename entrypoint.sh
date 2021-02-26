#!/bin/sh -l
#
# SPDX-License-Identifier: Apache-2.0
# Copyright 2021, Intel Corporation

set -e
set -x

echo "$1"

project_dir=${WORKDIR:-/pmemkv-bench}

echo "run basic test"
pytest-3 -v ${project_dir}/tests/test.py

