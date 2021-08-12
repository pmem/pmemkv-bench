#!/bin/sh -l
#
# SPDX-License-Identifier: Apache-2.0
# Copyright 2021, Intel Corporation

set -e
set -x

echo "$1"

export KV_BENCH_TEST_PATH=${KV_BENCH_TEST_PATH}
project_dir=${WORKDIR:-/pmemkv-bench}
cd ${project_dir}

echo "run checkers"
make check-cppformat
make check-pyformat

echo "run basic test"
pytest-3 ./tests/test.py -v --log-level=info -x
