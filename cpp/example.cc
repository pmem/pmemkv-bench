#include <iostream>
#include "libpmemkv.h"

#define LOG(msg) std::cout << msg << "\n"

using namespace pmemkv;

int main() {
    LOG("Opening datastore");
    KVEngine* kv = KVEngine::Open("kvtree3", "/dev/shm/pmemkv", 1073741824);  // 1 GB pool

    LOG("Putting new key");
    KVStatus s = kv->Put("key1", "value1");
    assert(s == OK && kv->Count() == 1);

    LOG("Reading key back");
    string value;
    s = kv->Get("key1", &value);
    assert(s == OK && value == "value1");

    LOG("Iterating existing keys");
    kv->Put("key2", "value2");
    kv->Put("key3", "value3");
    kv->Each([](void* context, int32_t kb, const char* k, int32_t vb, const char* v) {
        LOG("  visited: " << k);
    });

    LOG("Removing existing key");
    s = kv->Remove("key1");
    assert(s == OK && !kv->Exists("key1"));

    LOG("Closing datastore");
    delete kv;
    return 0;
}
