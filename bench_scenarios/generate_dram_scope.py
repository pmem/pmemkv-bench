#!/usr/bin/env python3
#
# SPDX-License-Identifier: Apache-2.0
# Copyright 2021, Intel Corporation

# This script implements generate() method, which may be invoked by run_benchmark.py directly,
# or used as standalone application, which prints configuration json to stdout.
# Such once generated json may be saved and passed to run_benchmark.py as a parameter

import argparse
import json
import itertools

benchmarks = [
    "fillrandom,readrandom",
    "fillseq,readseq",
    "fillseq,readwhilewriting",
    "fillseq,readrandomwriterandom",
]

key_size = [8]
value_size = [8, 128, 256, 512, 1024]
number_of_elements = int(10 * 1e6)


def concurrent_engines():

    number_of_threads = [1, 4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 56]
    engine = ["blackhole", "dram_vcmap"]

    result = itertools.product(
        benchmarks, key_size, value_size, number_of_threads, engine
    )
    return list(result)


def generate():
    benchmarks = []
    benchmarks.extend(concurrent_engines())
    benchmarks_configuration = []
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
            },
            "numactl": {
                "--cpubind": "1",
            },
            "emon": "True",
        }

        benchmarks_configuration.append(benchmark_settings)

    return benchmarks_configuration


if __name__ == "__main__":
    help_msg = """
Test case generator for dram pmemkv engines.
"""
    argparse.ArgumentParser(
        description=help_msg, formatter_class=argparse.RawTextHelpFormatter
    ).parse_args()

    output = generate()
    print(json.dumps(output, indent=4))
