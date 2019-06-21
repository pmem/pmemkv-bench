#include <iostream>
#include <assert.h>

#include "libpmemkv.hpp"

#define LOG(msg) std::cout << msg << "\n"

using namespace pmem::kv;

int main()
{
	LOG("Starting engine");
	const std::string PATH = "/dev/shm/";
	const size_t size = 1024ULL * 1024ULL * 1024ULL * 1;
	int ret = 0;
	size_t cnt = 0;

	pmemkv_config *cfg = pmemkv_config_new();

	if (cfg == nullptr)
		throw std::runtime_error("creating config failed");

	auto cfg_s = pmemkv_config_put(cfg, "path", PATH.c_str(), PATH.size() + 1);
	if (cfg_s != PMEMKV_STATUS_OK)
		throw std::runtime_error("putting 'path' to config failed");

	cfg_s = pmemkv_config_put(cfg, "size", &size, sizeof(size));
	if (cfg_s != PMEMKV_STATUS_OK)
		throw std::runtime_error("putting 'size' to config failed");

	db *kv = new db;
	status s = kv->open("vsmap", cfg);
	if (s != status::OK)
		throw std::runtime_error("open failed");

	pmemkv_config_delete(cfg);

	LOG("Putting new key");
	s = kv->put("key1", "value1");
	assert(s == status::OK && kv->count(cnt) == status::OK);
	assert(cnt == 1);

	LOG("Reading key back");
	std::string value;
	s = kv->get("key1", &value);
	assert(s == status::OK && value == "value1");

	LOG("Iterating existing keys");
	kv->put("key2", "value2");
	kv->put("key3", "value3");
	kv->all([](string_view k) { LOG("  visited: " << k.data()); });

	LOG("Removing existing key");
	s = kv->remove("key1");
	assert(s == status::OK && kv->exists("key1") == status::NOT_FOUND);

	LOG("Stopping engine");
	delete kv;
	return 0;
}
