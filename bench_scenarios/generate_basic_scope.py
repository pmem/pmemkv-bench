import json
import itertools


def generate():
    benchmarks = [
        "fillseq",
        "fillrandom",
        "fillseq,readrandom,readrandom",
        "fillrandom,readrandom, readrandom",
        "fillseq,readseq,readseq",
        "fillrandom,readseq,readseq",
        "readwhilewriting",
        "readrandomwriterandom",
    ]

    size = [8, 128]

    number_od_elements = 100000000

    number_of_threads = [1, 4, 8, 12, 18, 24]
    engine = ["cmap", "csmap", "radix", "stree"]

    result = itertools.product(benchmarks, size, number_of_threads, engine)
    s_result = list(result)
    print(len(s_result))
    benches = []
    for b in s_result:
        benchmark_settings = {
            "env": {},
            "params": [
                f"--benchmarks={b[0]}",
                f"--value_size={b[1]}",
                f"--threads={b[2]}",
                f"--engine={b[3]}",
                f"--num={number_od_elements}",
                "--db=/mnt/pmem0",
                "--db_size_in_gb=6",
            ],
        }

        benches.append(benchmark_settings)

    return benches
