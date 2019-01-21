#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include "libpmemkv.h"

#define LOG(msg) printf("%s\n", msg)
#define MAX_VAL_LEN 64

void StartFailureCallback(void* context, const char* engine, const char* config, const char* msg) {
    printf("ERROR: %s\n", msg);
    exit(-1);
}

void AllCallback(void* context, int kb, const char* k) {
    printf("   visited: %s\n", k);
}

int main() {
    LOG("Starting engine");
    KVEngine* kv = kvengine_start(NULL, "kvtree3", "{\"path\":\"/dev/shm/pmemkv\"}", &StartFailureCallback);

    LOG("Putting new key");
    char* key1 = "key1";
    char* value1 = "value1";
    KVStatus s = kvengine_put(kv, strlen(key1), key1, strlen(value1), value1);
    assert(s == OK && kvengine_count(kv) == 1);

    LOG("Reading key back");
    char val[MAX_VAL_LEN];
    s = kvengine_get_copy(kv, strlen(key1), key1, MAX_VAL_LEN, val);
    assert(s == OK && !strcmp(val, "value1"));

    LOG("Iterating existing keys");
    char* key2 = "key2";
    char* value2 = "value2";
    char* key3 = "key3";
    char* value3 = "value3";
    kvengine_put(kv, strlen(key2), key2, strlen(value2), value2);
    kvengine_put(kv, strlen(key3), key3, strlen(value3), value3);
    kvengine_all(kv, NULL, &AllCallback);

    LOG("Removing existing key");
    s = kvengine_remove(kv, strlen(key1), key1);
    assert(s == OK && kvengine_exists(kv, strlen(key1), key1) == NOT_FOUND);

    LOG("Stopping engine");
    kvengine_stop(kv);
    return 0;
}
