#!/usr/bin/env python3
#
# SPDX-License-Identifier: Apache-2.0
# Copyright 2021, Intel Corporation

# This script implements generate() method, which may be invoked by run_benchmark.py directly,
# or used as standalone application, which prints configuration json to stdout.
# Such once generated json may be saved and passed to run_benchmark.py as a parameter

import json
import itertools
import os

benchmarks = [
    "fillseq",
    "fillrandom",
    "fillseq,readrandom,readrandom",
    "fillrandom,readrandom,readrandom",
    "fillseq,readseq,readseq",
    "fillrandom,readseq,readseq",
    "fillseq,readwhilewriting",
    "fillseq,readrandomwriterandom",
]
key_size = [8]
value_size = [8, 128, 1024]
number_of_elements = 1000000


def concurrent_engines():

    number_of_threads = [1, 4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 56]
    engine = ["vcmap"]

    result = itertools.product(
        benchmarks, key_size, value_size, number_of_threads, engine
    )

    return list(result)


def single_threaded_engines():
    number_of_threads = [1]
    engine = ["vsmap"]
    result = itertools.product(
        benchmarks, key_size, value_size, number_of_threads, engine
    )
    return list(result)


def generate():
    benchmarks = []
    benchmarks.extend(single_threaded_engines())
    benchmarks.extend(concurrent_engines())
    benchmarks_configuration = []
    db_path = os.getenv("PMEMKV_BENCH_DB_PATH", "/mnt/pmem1")
    for benchmark in benchmarks:
        benchmark_settings = {
            "env": {},
            "pmemkv_bench": {
                "--benchmarks": f"{benchmark[0]}",
                "--key_size": f"{benchmark[1]}",
                "--value_size": f"{benchmark[2]}",
                "--threads": f"{benchmark[3]}",
                "--engine": f"{benchmark[4]}",
                "--num": f"{number_of_elements}",
                "--db": db_path,
                "--db_size_in_gb": "500",
            },
            "numactl": {
                "--cpubind": f"file:{os.path.dirname(db_path)}",
            },
        }

        benchmarks_configuration.append(benchmark_settings)

    return benchmarks_configuration


if __name__ == "__main__":
    output = generate()
    print(json.dumps(output, indent=4))
