#!/bin/sh -l
#
# SPDX-License-Identifier: Apache-2.0
# Copyright 2021, Intel Corporation

set -e
set -x

echo "$1"

project_dir=/pmemkv-bench

echo "run basic test"
python3 ${project_dir}/run_benchmark.py ${project_dir}/bench_scenarios/basic.json

