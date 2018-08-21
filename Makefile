.ONESHELL:

reset:
	rm -rf /dev/shm/pmemkv /tmp/pmemkv

clean: reset
	rm -rf pmemkv_bench ./c/baseline ./c/example ./cpp/baseline ./cpp/example ./java/*.class

bench: clean
	g++ ./bench/db_bench.cc ./bench/port/port_posix.cc ./bench/util/env.cc ./bench/util/env_posix.cc ./bench/util/histogram.cc ./bench/util/logging.cc ./bench/util/status.cc -o pmemkv_bench /usr/local/lib/libpmemkv.so -I/usr/local/include -I./bench/include -I./bench -I./bench/util -O2 -std=c++11 -DOS_LINUX -fno-builtin-memcmp -march=native -ldl -lpthread -DNDEBUG
	PMEM_IS_PMEM_FORCE=1 ./pmemkv_bench --db=/dev/shm/pmemkv --db_size_in_gb=1 --histogram=1
	rm -rf /dev/shm/pmemkv

baseline_c: clean
	cd c
	echo 'Build and run baseline.c'

baseline_cpp: clean
	cd cpp
	g++ baseline.cc -o baseline /usr/local/lib/libpmemkv.so -I/usr/local/include -O2 -std=c++11 -DOS_LINUX -fno-builtin-memcmp -march=native -ldl -lpthread
	PMEM_IS_PMEM_FORCE=1 ./baseline

example_cpp: clean
	cd cpp
	g++ example.cc -o example /usr/local/lib/libpmemkv.so -I/usr/local/include -O2 -std=c++11 -DOS_LINUX -fno-builtin-memcmp -march=native -ldl -lpthread
	PMEM_IS_PMEM_FORCE=1 ./example

baseline_java: clean
	cd java
	javac -cp ../../pmemkv-java/target/*.jar Baseline.java
	PMEM_IS_PMEM_FORCE=1 java -Xms1G -cp .:`find ../../pmemkv-java/target -name *.jar` -Djava.library.path=/usr/local/lib Baseline

baseline_nodejs: clean
	cd nodejs
	PMEM_IS_PMEM_FORCE=1 node baseline.js

baseline_ruby: clean
	cd ruby
	PMEM_IS_PMEM_FORCE=1 ruby baseline.rb

