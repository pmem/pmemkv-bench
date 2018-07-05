.ONESHELL:

reset:
	rm -rf /dev/shm/pmemkv /tmp/pmemkv

clean: reset
	rm -rf ./java/*.class

baseline_c: clean
	cd c
	echo 'Build and run baseline.c'

baseline_cpp: clean
	cd cpp
	echo 'Build and run baseline.cc'

baseline_java: clean
	cd java
	javac -cp ../../pmemkv-java/target/*.jar Baseline.java
	PMEM_IS_PMEM_FORCE=1 java -cp .:`find ../../pmemkv-java/target -name *.jar` -Djava.library.path=/usr/local/lib Baseline

baseline_nodejs: clean
	cd nodejs
	PMEM_IS_PMEM_FORCE=1 node baseline.js

baseline_ruby: clean
	cd ruby
	PMEM_IS_PMEM_FORCE=1 ruby baseline.rb

db_bench: clean
	cd db_bench
	echo 'Build db_bench'
