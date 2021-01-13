# pmemkv-bench
Benchmark for pmemkv and its underlying libraries, based on leveldb's db_bench.

*This is experimental pre-release software and should not be used in
production systems. APIs and file formats may change at any time without
preserving backwards compatibility. All known issues and limitations
are logged as GitHub issues.*

# Benchmarking

The `pmemkv_bench` utility provides some standard read & write benchmarks. This is
based on the `db_bench` utility included with LevelDB and RocksDB, although the
list of supported parameters is slightly different.

The `pmemkv-bench` may clear or remove pool passed in `--db` parameter, so pool, poolset or DAX
device which contain existing data shouldn't be used.

To build `pmemkv_bench`:

```
make bench
```

Supported runtime parameters:

```
--engine=<name>            (storage engine name, default: cmap)
--db=<location>            (path to persistent pool, default: /dev/shm/pmemkv)
                           (note: file on DAX filesystem, DAX device, or poolset file)
--db_size_in_gb=<integer>  (size of persistent pool to create in GB, default: 0)
                           (note: always use 0 with poolset or device DAX configs)
--histogram=<0|1>          (show histograms when reporting latencies)
--num=<integer>            (number of keys to place in database, default: 1000000)
--reads=<integer>          (number of read operations, default: 1000000)
--threads=<integer>        (number of concurrent threads, default: 1)
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

Benchmarking on emulated persistent memory:

```
PMEM_IS_PMEM_FORCE=1 ./pmemkv_bench --db=/dev/shm/pmemkv --db_size_in_gb=1
```

Benchmarking on filesystem DAX:

```
./pmemkv_bench --db=/mnt/pmem/pmemkv --db_size_in_gb=1
```

Benchmarking on device DAX:

```
./pmemkv_bench --db=/dev/dax1.0
```

Benchmarking with poolset:

```
./pmemkv_bench --db=~/pmemkv.poolset
```

## Setting up environment

If pmemkv is installed in some non-standard path, `LD_LIBRARY_PATH` variable should be set
to the directory which contains `libpmemkv.so.1` file

```
export LD_LIBRARY_PATH=</path/to/libpmemkv>
```
