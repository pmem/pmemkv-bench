# SPDX-License-Identifier: Apache-2.0
# Copyright 2017-2021, Intel Corporation

.ONESHELL:

bench: CFLAGS = $(shell pkg-config --cflags libpmemkv libpmempool) -DOS_LINUX -fno-builtin-memcmp -march=native -DNDEBUG -O2 -std=c++11
bench: LDFLAGS = -ldl -lpthread $(shell pkg-config --libs libpmemkv libpmempool)
CPP_FILES = $(shell find . -iname "*.h" -o -iname "*.cc" -o -iname "*.cpp" -o -iname "*.hpp")
PYTHON_FILES = $(shell find . -iname "*.py")
KV_BENCH_TEST_PATH ?= /dev/shm/pmemkv_test_db


.PHONY: cppformat check-cppformat $(CPP_FILES) pyformat check-pyformat $(PYTHON_FILES)

bench: clean
	g++ ./bench/db_bench.cc ./bench/port/port_posix.cc ./bench/util/env.cc ./bench/util/env_posix.cc \
		./bench/util/histogram.cc ./bench/util/logging.cc ./bench/util/status.cc ./bench/util/testutil.cc \
		-o pmemkv_bench -I./bench/include -I./bench -I./bench/util $(CFLAGS) $(LDFLAGS)

reset: clean
	rm -rf "${KV_BENCH_TEST_PATH}"

clean:
	rm -rf pmemkv_bench

run_bench: bench
	PMEM_IS_PMEM_FORCE=1 ./pmemkv_bench --db="${KV_BENCH_TEST_PATH}" --db_size_in_gb=1 --histogram=1

cppformat: $(CPP_FILES)

$(CPP_FILES):
	clang-format-11 -i $@

check-cppformat:
	@for src in $(CPP_FILES) ; do \
		clang-format-11 --verbose --Werror -n "$$src" || exit 1 ;\
	done

pyformat: $(PYTHON_FILES)

$(PYTHON_FILES):
	python3 -m black $@

check-pyformat:
	@for src in $(PYTHON_FILES) ; do \
		echo "$$src" ;\
		python3 -m black "$$src" --check || exit 1 ;\
	done
