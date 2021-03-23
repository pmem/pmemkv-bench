#!/usr/bin/env python3
#
# SPDX-License-Identifier: Apache-2.0
# Copyright 2021, Intel Corporation

import os, sys
import pytest
import json
import tempfile

tests_path = os.path.dirname(os.path.realpath(__file__))
project_path = os.path.dirname(tests_path)
sys.path.append(project_path)
import run_benchmark as rb

build_configuration = {
    "db_bench": {
        "repo_url": project_path,
        "commit": "HEAD",
        "env": {},
    },
    "pmemkv": {
        "repo_url": "https://github.com/pmem/pmemkv.git",
        "commit": "HEAD",
        "cmake_params": [
            "-DCMAKE_BUILD_TYPE=Release",
            "-DENGINE_CMAP=1",
            "-DENGINE_CSMAP=1",
            "-DENGINE_RADIX=1",
            "-DENGINE_STREE=1",
            "-DENGINE_ROBINHOOD=1",
            "-DENGINE_VCMAP=1",
            "-DBUILD_JSON_CONFIG=1",
            "-DCXX_STANDARD=20",
            "-DBUILD_TESTS=OFF",
            "-DBUILD_DOC=OFF",
            "-DBUILD_EXAMPLES=OFF",
        ],
        "env": {"CC": "gcc", "CXX": "g++"},
    },
    "libpmemobjcpp": {
        "repo_url": "https://github.com/pmem/libpmemobj-cpp.git",
        "commit": "HEAD",
        "cmake_params": [
            "-DBUILD_EXAMPLES=OFF",
            "-DBUILD_TESTS=OFF",
            "-DBUILD_DOC=OFF",
            "-DBUILD_BENCHMARKS=OFF",
            "-DCMAKE_BUILD_TYPE=Release",
        ],
        "env": {"CC": "gcc", "CXX": "g++"},
    },
}


def create_config_file(configuration):
    tf = tempfile.NamedTemporaryFile(suffix=".json", mode="w", delete=False)
    json.dump(configuration, tf)
    tf.close()
    return tf


def execute_run_benchmark(build_configuration, benchmark_configuration):
    build_config_file = create_config_file(build_configuration)
    test_config_file = create_config_file(benchmark_configuration)
    sys.argv = ["dummy.py", build_config_file.name, test_config_file.name]
    try:
        result = rb.main()
    except Exception as e:
        assert False, f"run-bench raised exception: {e}"


def test_help():
    """ Simple sanity check for -h option of run_benchmark.py. """
    sys.argv = ["dummy.py", "-h"]
    with pytest.raises(SystemExit) as e:
        result = rb.main()
    assert e.type == SystemExit
    assert e.value.code == 0


@pytest.mark.parametrize(
    "engine,test_path,benchmarks",
    [
        (
            "blackhole",
            os.getenv("TEST_PATH", "/dev/shm/pmemkv"),
            "fillrandom,readrandom",
        ),
    ],
)
def test_numactl(engine, test_path, benchmarks):
    """Basic integration test for run_benchmark.py. It runs full
    benchmarking process for arbitrarily chosen parameters.
    """

    benchmark_configuration = [
        {
            "env": {"PMEM_IS_PMEM_FORCE": "1"},
            "pmemkv_bench": {
                "--db": test_path,
                "--db_size_in_gb": "1",
                "--benchmarks": benchmarks,
                "--engine": engine,
                "--num": "100",
                "--value_size": "8",
                "--threads": "2",
            },
            "numactl": {
                "--physcpubind": "1",
            },
        },
    ]

    execute_run_benchmark(build_configuration, benchmark_configuration)


@pytest.mark.parametrize(
    "engine,test_path,benchmarks",
    [
        ("cmap", os.getenv("TEST_PATH", "/dev/shm/pmemkv"), "fillrandom,readrandom"),
        ("csmap", os.getenv("TEST_PATH", "/dev/shm/pmemkv"), "fillrandom,readrandom"),
        (
            "vcmap",
            os.path.dirname(os.getenv("TEST_PATH", "/dev/shm/pmemkv")),
            "fillrandom,readrandom",
        ),
        (
            "vsmap",
            os.path.dirname(os.getenv("TEST_PATH", "/dev/shm/pmemkv")),
            "fillrandom,readrandom",
        ),
    ],
)
def test_json(engine, test_path, benchmarks):
    """Basic integration test for run_benchmark.py. It runs full
    benchmarking process for arbitrarily chosen parameters.
    """

    benchmark_configuration = [
        {
            "env": {"PMEM_IS_PMEM_FORCE": "1"},
            "pmemkv_bench": {
                "--db": test_path,
                "--db_size_in_gb": "1",
                "--benchmarks": benchmarks,
                "--engine": engine,
                "--num": "100",
                "--value_size": "8",
                "--key_size": "8",
                "--threads": "2",
            },
        },
        {
            "env": {},
            "pmemkv_bench": {
                "--db": os.getenv("TEST_PATH", "/dev/shm/pmemkv"),
                "--db_size_in_gb": "2",
                "--benchmarks": "fillseq",
                "--engine": "radix",
                "--num": "100",
                "--value_size": "1024",
                "--key_size": "128",
                "--threads": "1",
            },
        },
    ]

    execute_run_benchmark(build_configuration, benchmark_configuration)
