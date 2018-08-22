#include <iostream>
#include "libpmemkv.h"

#define LOG(msg) std::cout << msg << "\n"

using namespace pmemkv;

int main() {
    LOG("Opening datastore");
    KVEngine* kv = KVEngine::Open("kvtree2", "/dev/shm/pmemkv", PMEMOBJ_MIN_POOL);

    LOG("Putting new value");
    KVStatus s = kv->Put("key1", "value1");
    assert(s == OK);
    string value;
    s = kv->Get("key1", &value);
    assert(s == OK && value == "value1");

    LOG("Replacing existing value");
    string value2;
    s = kv->Get("key1", &value2);
    assert(s == OK && value2 == "value1");
    s = kv->Put("key1", "value_replaced");
    assert(s == OK);
    string value3;
    s = kv->Get("key1", &value3);
    assert(s == OK && value3 == "value_replaced");

    LOG("Removing existing value");
    s = kv->Remove("key1");
    assert(s == OK);
    string value4;
    s = kv->Get("key1", &value4);
    assert(s == NOT_FOUND);

    LOG("Closing datastore");
    delete kv;

    LOG("Finished successfully");
    return 0;
}
