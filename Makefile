# SPDX-License-Identifier: Apache-2.0
# Copyright 2017-2020, Intel Corporation

.ONESHELL:

bench: CFLAGS = $(shell pkg-config --cflags libpmemkv) -DOS_LINUX -fno-builtin-memcmp -march=native -DNDEBUG -O2 -std=c++11
bench: LDFLAGS = -ldl -lpthread $(shell pkg-config --libs libpmemkv)

reset:
	rm -rf /dev/shm/pmemkv /tmp/pmemkv

clean: reset
	rm -rf pmemkv_bench

bench: reset
	g++ ./bench/db_bench.cc ./bench/port/port_posix.cc ./bench/util/env.cc ./bench/util/env_posix.cc ./bench/util/histogram.cc ./bench/util/logging.cc ./bench/util/status.cc ./bench/util/testutil.cc -o pmemkv_bench -I./bench/include -I./bench -I./bench/util $(CFLAGS) $(LDFLAGS)

run_bench: bench
	PMEM_IS_PMEM_FORCE=1 ./pmemkv_bench --db=/dev/shm/pmemkv --db_size_in_gb=1 --histogram=1
