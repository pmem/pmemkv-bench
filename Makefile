.ONESHELL:

reset:
	rm -rf /dev/shm/pmemkv /tmp/pmemkv

clean: reset
	rm -rf pmemkv_bench ./c/*.bin ./cpp/*.bin ./java/*.class

bench: reset
	g++ ./bench/db_bench.cc ./bench/port/port_posix.cc ./bench/util/env.cc ./bench/util/env_posix.cc ./bench/util/histogram.cc ./bench/util/logging.cc ./bench/util/status.cc ./bench/util/testutil.cc -o pmemkv_bench -I./bench/include -I./bench -I./bench/util -O2 -std=c++11 -DOS_LINUX -fno-builtin-memcmp -march=native -DNDEBUG -ldl -lpthread -lpmemkv
	PMEM_IS_PMEM_FORCE=1 ./pmemkv_bench --db=/dev/shm/pmemkv --db_size_in_gb=1 --histogram=1
	$(MAKE) reset

baseline_c: reset
	cd c
	echo 'Build and run baseline.c'
	cd .. && $(MAKE) reset

baseline_cpp: reset
	cd cpp
	g++ baseline.cc -o baseline.bin -O2 -std=c++11 -lpmemkv
	PMEM_IS_PMEM_FORCE=1 ./baseline.bin
	cd .. && $(MAKE) reset

baseline_java: reset
	cd java
	javac -cp ../../pmemkv-java/target/*.jar Baseline.java
	PMEM_IS_PMEM_FORCE=1 java -Xms1G -cp .:`find ../../pmemkv-java/target -name *.jar` -Djava.library.path=/usr/local/lib Baseline
	cd .. && $(MAKE) reset

baseline_nodejs: reset
	cd nodejs
	PMEM_IS_PMEM_FORCE=1 node baseline.js
	cd .. && $(MAKE) reset

baseline_ruby: reset
	cd ruby
	PMEM_IS_PMEM_FORCE=1 ruby baseline.rb
	cd .. && $(MAKE) reset

baseline_python: reset
	cd python
	PMEM_IS_PMEM_FORCE=1 python3 baseline.py
	cd .. && $(MAKE) reset

iteration_cpp: reset
	cd cpp
	g++ iteration.cc -o iteration.bin -O2 -std=c++11 -lpmemkv
	PMEM_IS_PMEM_FORCE=1 ./iteration.bin
	cd .. && $(MAKE) reset

iteration_java: reset
	cd java
	javac -cp ../../pmemkv-java/target/*.jar Iteration.java
	PMEM_IS_PMEM_FORCE=1 java -Xms1G -cp .:`find ../../pmemkv-java/target -name *.jar` -Djava.library.path=/usr/local/lib Iteration
	cd .. && $(MAKE) reset

iteration_python: reset
	cd python
	PMEM_IS_PMEM_FORCE=1 python3 iteration.py
	cd .. && $(MAKE) reset

storage_efficiency: reset
	cd ruby
	PMEM_IS_PMEM_FORCE=1 ruby storage_efficiency.rb
	cd .. && $(MAKE) reset
