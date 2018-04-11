.ONESHELL:

reset:
	rm -rf /dev/shm/pmemkv /tmp/pmemkv

clean: reset
	rm -rf ./java/*.class

java_bench: clean
	cd java
	javac -cp ../../pmemkv-java/target/*.jar Bench.java
	PMEM_IS_PMEM_FORCE=1 java -cp .:`find ../../pmemkv-java/target -name *.jar` -Djava.library.path=/usr/local/lib Bench

nodejs_bench: clean
	cd nodejs
	PMEM_IS_PMEM_FORCE=1 node bench.js

ruby_bench: clean
	cd ruby
	PMEM_IS_PMEM_FORCE=1 ruby bench.rb
