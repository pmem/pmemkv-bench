# pmemkv-bench

[![.github/workflows/main.yml](https://github.com/pmem/pmemkv-bench/actions/workflows/main.yml/badge.svg)](https://github.com/pmem/pmemkv-bench/actions/workflows/main.yml)
[![PMEMKV-BENCH version](https://img.shields.io/github/tag/pmem/pmemkv-bench.svg)](https://github.com/pmem/pmemkv-bench/releases/latest)

Benchmark for [libpmemkv](https://github.com/pmem/pmemkv/) and its underlying libraries,
based on [leveldb's db_bench](https://github.com/google/leveldb).

The `pmemkv_bench` utility provides some standard read, write & remove benchmarks. It's
based on the `db_bench` utility included with LevelDB and RocksDB, although the
list of supported parameters is slightly different.

We always try to improve this benchmark and keep it up-to-date with libpmemkv.
Please don't fully rely on API and the results produced by this tool.
If you have any questions, improvement ideas or you found a bug,
please file a report in the [issues tab](https://github.com/pmem/pmemkv-bench/issues).
Contributions are also welcome - take a look at our [CONTRIBUTING.md](CONTRIBUTING.md).

**Note:**
>The `pmemkv-bench` may clear pool passed in `--db` parameter, so pool, poolset or DAX
>device which contain existing data shouldn't be used.

## Table of contents

1. [Build](#build)
    - [Prerequisites](#prerequisites)
    - [Setting up environment](#setting-up-environment)
    - [Compile](#compile)
2. [Execute](#execute)
    - [Various Pools](#various-pools)
    - [Runtime Parameters](#runtime-parameters)
3. [Contact us](#contact-us)

## Build

### Prerequisites

* **Linux 64-bit** (OSX and Windows are not yet supported)
* [**libpmemkv**](https://github.com/pmem/pmemkv) - library tested in this benchmark;
    at best the most recent release or version from master branch
* **libpmempool**, which is part of [PMDK](https://github.com/pmem/pmdk) - tool to manage persistent pools
* [**python3**](https://www.python.org/download/releases/3.0/) - for executing additional python scripts (and tests)
* Used only for **development**:
	* [**clang-format-11**](https://clang.llvm.org/docs/ClangFormat.html) -
        to format and check coding style, version 11 is required

See our **[Dockerfile](./Dockerfile)** (used e.g. on our CI system) to get an idea what packages
are required to build and run pmemkv-bench.

### Setting up environment

**Makefile** tries to find required packages (especially libpmemkv and libpmempool)
using pkg-config. If dependencies are not installed in the system
`PKG_CONFIG_PATH` variable has to be set to point to .pc files.

For **execution**, additionally `LD_LIBRARY_PATH` variable should be set
to the directory which contains `libpmemkv.so.1` file, e.g.:

```sh
export PKG_CONFIG_PATH=${PKG_CONFIG_PATH}:</path/to/libpmemkv/pkgconfig/dir>
export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:</path/to/libpmemkv/lib/dir>
```

### Compile
To build `pmemkv_bench`, you can simple run:

```sh
make bench
```

## Execute

To simply run `pmemkv-bench` on DRAM:

```sh
PMEM_IS_PMEM_FORCE=1 ./pmemkv_bench --db=/dev/shm/pmemkv --db_size_in_gb=1
```

or using make command:

```sh
make run_bench
```

**Alternatively** you can run building selected version of pmemkv
(and required by it a libpmemobj-cpp library) and run benchmark scenarios
using python script (available in project's root directory):

```sh
python3 run_benchmark.py <build_config_file> <bench_scenarios_file>
```

Example usage of this script is also shown in
[one of our tests](./tests/test.py#L49).

### Various Pools

Benchmarking on filesystem DAX (fsdax, mounted e.g. on /mnt/pmem):

```sh
./pmemkv_bench --db=/mnt/pmem/pmemkv --db_size_in_gb=1
```

Benchmarking on device DAX (dev-dax):

```sh
./pmemkv_bench --db=/dev/dax1.0
```

Benchmarking with poolset (to read more, see PMDK's manpage
[poolset(5)](https://pmem.io/pmdk/manpages/linux/master/poolset/poolset.5)):

```sh
./pmemkv_bench --db=~/pmemkv.poolset
```

**Remember:**
>The `pmemkv-bench` may clear pool passed in `--db` parameter, so pool, poolset or DAX
>device which contain existing data shouldn't be used.

### Runtime Parameters

All of supported `pmemkv-bench`'s parameters are described in command's help
(see it e.g. in [bench's sources](./bench/db_bench.cc#L36)).

Nonetheless, the most important runtime parameters are:

```
--engine=<name>            (storage engine name, default: cmap)
--db=<location>            (path to persistent pool, default: /dev/shm/pmemkv)
                           (note: file on DAX filesystem, DAX device, or poolset file)
--db_size_in_gb=<integer>  (size of persistent pool to create in GB, default: 0)
                           (note: for existing poolset or device DAX configs use 0 or leave default value)
                           (note: when pool path is non-existing, value should be > 0)
--histogram=<0|1>          (show histograms when reporting latencies)
--num=<integer>            (number of keys to place in database, default: 1000000)
--reads=<integer>          (number of read operations, default: 1000000)
--threads=<integer>        (number of concurrent threads, default: 1)
--key_size=<integer>       (size of keys in bytes, default: 16)
--value_size=<integer>     (size of values in bytes, default: 100)
--benchmarks=<name>,       (comma-separated list of benchmarks to run)
    fillseq                (load N values in sequential key order)
    fillrandom             (load N values in random key order)
    overwrite              (replace N values in random key order)
    readseq                (read N values in sequential key order)
    readrandom             (read N values in random key order)
    readmissing            (read N missing values in random key order)
    deleteseq              (delete N values in sequential key order)
    deleterandom           (delete N values in random key order)
    readwhilewriting       (1 writer, N threads doing random reads)
    readrandomwriterandom  (N threads doing random-read, random-write)
```

## Contact us

For more information about **pmemkv** or **pmemkv-bench**, contact Igor Chorążewicz (igor.chorazewicz@intel.com),
Piotr Balcer (piotr.balcer@intel.com) or post on our **#pmem** Slack channel using
[this invite link](https://join.slack.com/t/pmem-io/shared_invite/enQtNzU4MzQ2Mzk3MDQwLWQ1YThmODVmMGFkZWI0YTdhODg4ODVhODdhYjg3NmE4N2ViZGI5NTRmZTBiNDYyOGJjYTIyNmZjYzQxODcwNDg) or [Google group](https://groups.google.com/group/pmem).
