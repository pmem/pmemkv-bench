#!/usr/bin/env python3
#
# SPDX-License-Identifier: Apache-2.0
# Copyright 2021, Intel Corporation

import os, sys
import pytest
import json
import tempfile
import jsonschema

DEFAULT_TEST_FILE = "/dev/shm/pmemkv_test_db"
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

    return result


def test_help():
    """Simple sanity check for -h option of run_benchmark.py."""

    sys.argv = ["dummy.py", "-h"]
    with pytest.raises(SystemExit) as e:
        result = rb.main()
    assert e.type == SystemExit
    assert e.value.code == 0


@pytest.mark.parametrize(
    "engine,test_path,benchmarks",
    [
        (
            "cmap",
            os.getenv("KV_BENCH_TEST_PATH", DEFAULT_TEST_FILE),
            "fillrandom,readrandom",
        ),
        (
            "csmap",
            os.getenv("KV_BENCH_TEST_PATH", DEFAULT_TEST_FILE),
            "fillrandom,readrandom",
        ),
        (
            "blackhole",
            os.getenv("KV_BENCH_TEST_PATH", DEFAULT_TEST_FILE),
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
                "--key_size": "16",
                "--threads": "2",
            },
            "numactl": {
                "--physcpubind": "1",
            },
            "cleanup": 1,
        },
    ]

    res = execute_run_benchmark(build_configuration, benchmark_configuration)
    assert len(res) == 1


@pytest.mark.parametrize(
    "engine,test_path,benchmarks",
    [
        (
            "cmap",
            os.getenv("KV_BENCH_TEST_PATH", DEFAULT_TEST_FILE),
            "fillrandom,readrandom",
        ),
        (
            "cmap",
            os.getenv("KV_BENCH_TEST_PATH", DEFAULT_TEST_FILE),
            "readrandom,fillrandom,readrandom",
        ),
        (
            "csmap",
            os.getenv("KV_BENCH_TEST_PATH", DEFAULT_TEST_FILE),
            "fillrandom,readrandom",
        ),
        (
            "vcmap",
            os.path.dirname(os.getenv("KV_BENCH_TEST_PATH", DEFAULT_TEST_FILE)),
            "fillrandom,readrandom",
        ),
        (
            "vsmap",
            os.path.dirname(os.getenv("KV_BENCH_TEST_PATH", DEFAULT_TEST_FILE)),
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
            "cleanup": 1,
        },
        {
            "env": {},
            "pmemkv_bench": {
                "--db": os.getenv("KV_BENCH_TEST_PATH", DEFAULT_TEST_FILE),
                "--db_size_in_gb": "2",
                "--benchmarks": "fillseq",
                "--engine": "radix",
                "--num": "100",
                "--value_size": "1024",
                "--key_size": "128",
                "--threads": "1",
            },
            "cleanup": 1,
        },
    ]
    res = execute_run_benchmark(build_configuration, benchmark_configuration)
    assert len(res) == 2


@pytest.mark.parametrize(
    "bench1,cleanup1,bench2,expected",
    [
        ("fillseq", 0, "readseq", 100),
        ("fillrandom", 1, "readrandom", 0),
        ("readrandom", 1, "readrandom", 0),
    ],
)
def test_benchmarks_separate_processes(bench1, cleanup1, bench2, expected):
    """Test two runs of run_benchmark.py. Each in separate process,
    some of them separated by a pool cleanup.
    """

    benchmark_configuration = [
        {
            "env": {},
            "pmemkv_bench": {
                "--db": os.getenv("KV_BENCH_TEST_PATH", DEFAULT_TEST_FILE),
                "--db_size_in_gb": "1",
                "--benchmarks": bench1,
                "--engine": "cmap",
                "--num": "100",
                "--value_size": "8",
                "--key_size": "8",
                "--threads": "2",
            },
            "cleanup": cleanup1,
        }
    ]

    execute_run_benchmark(build_configuration, benchmark_configuration)

    benchmark_configuration[0]["cleanup"] = 1
    benchmark_configuration[0]["pmemkv_bench"]["--benchmarks"] = bench2
    res = execute_run_benchmark(build_configuration, benchmark_configuration)

    # parse x from: "extra_data" : "(x of 100 found by one thread)"
    extra_data = res[0]["results"][0]["extra_data"]
    found = int(extra_data.split()[0][1:])
    assert found == expected


@pytest.mark.parametrize(
    "scenario",
    [
        "generate_obj_based_scope.py",
        "generate_dram_scope.py",
        "generate_memkind_based_scope.py",
    ],
)
def test_scenario(scenario):
    """Test if schema validation works as expected."""

    scenario_path = os.path.join(project_path, "bench_scenarios", scenario)
    schema_path = os.path.join(project_path, "bench_scenarios", "bench.schema.json")

    output = rb.load_scenarios(scenario_path)
    schema = None
    with open(schema_path, "r") as schema_file:
        schema = json.loads(schema_file.read())
    jsonschema.validate(instance=output, schema=schema)


@pytest.mark.parametrize(
    "test_description,input_json,schema",
    [
        (
            "missing required projects to build",
            {
                "db_bench": {
                    "repo_url": "project_path",
                    "commit": "HEAD",
                    "env": {},
                },
                "env": {"CC": "gcc", "CXX": "g++"},
            },
            "build.schema.json",
        ),
        (
            "missing params",
            [
                {
                    "env": {"PMEM_IS_PMEM_FORCE": "1"},
                },
            ],
            "bench.schema.json",
        ),
        (
            "missing params fields",
            [
                {
                    "env": {"PMEM_IS_PMEM_FORCE": "1"},
                    "pmemkv_bench": {
                        "--num": "100",
                    },
                },
            ],
            "bench.schema.json",
        ),
    ],
)
def test_wrong_input(input_json, schema, test_description):
    """Unit test for json schema validation"""

    print(f"Test: {test_description}")
    schema_path = os.path.join(project_path, "bench_scenarios", schema)

    json_test_path = create_config_file(input_json)
    with pytest.raises(jsonschema.exceptions.ValidationError):
        result = rb.load_scenarios(json_test_path.name, schema_path)
