#include <iostream>
#include <sys/time.h>
#include <vector>
#include "libpmemkv.h"

#define LOG(msg) std::cout << msg << "\n"

using namespace pmemkv;

static const int COUNT = 1000000;
static const string PATH = "/dev/shm/pmemkv";

static double current_seconds() {
    struct timeval tv;
    gettimeofday(&tv, NULL);
    return (tv.tv_sec) + (double) (tv.tv_usec) / 1000000;
}

struct EachCallbackContext {
    unsigned long failures;
};

void test_engine(const string engine, const std::vector<string> keys, const string value) {
    LOG("\nTesting " << engine << " for " + to_string(keys.size()) << " keys, value size is "
                     << value.length() << "...\n");
    std::remove(PATH.c_str());
    KVEngine* kv = KVEngine::Open(engine, PATH, 1024 * 1024 * 1024);

    LOG("Put (sequential series)");
    auto started = current_seconds();
    for (int i = 0; i < keys.size(); i++) {
        if (kv->Put(keys[i], value) != OK) {
            std::cout << "Out of space at key " << to_string(i) << "\n";
            exit(-42);
        }
    }
    LOG("   in " << current_seconds() - started << " sec");

    LOG("Get (sequential series)");
    int failures = 0;
    started = current_seconds();
    for (int i = 0; i < keys.size(); i++) {
        string value;
        if (kv->Get(keys[i], &value) != OK) failures++;
    }
    LOG("   in " << current_seconds() - started << " sec, failures=" + to_string(failures));

    LOG("Exists (sequential series)");
    failures = 0;
    started = current_seconds();
    for (int i = 0; i < keys.size(); i++) {
        if (kv->Exists(keys[i]) != OK) failures++;
    }
    LOG("   in " << current_seconds() - started << " sec, failures=" + to_string(failures));

    LOG("Each (one pass)");
    EachCallbackContext cxt = {keys.size()};
    auto cb = [](void* context, int32_t keybytes, int32_t valuebytes, const char* key, const char* value) {
        ((EachCallbackContext*) context)->failures--;
    };
    started = current_seconds();
    kv->Each(&cxt, cb);
    LOG("   in " << current_seconds() - started << " sec, failures=" + to_string(cxt.failures));

    LOG("EachLike (one pass, all keys match)");
    cxt = {keys.size()};
    started = current_seconds();
    kv->EachLike(".*", &cxt, cb);
    LOG("   in " << current_seconds() - started << " sec, failures=" + to_string(cxt.failures));

    LOG("EachLike (one pass, one key matches)");
    cxt = {1};
    started = current_seconds();
    kv->EachLike("1234", &cxt, cb);
    LOG("   in " << current_seconds() - started << " sec, failures=" + to_string(cxt.failures));

    delete kv;
}

int main() {
    // format all keys in advance
    std::vector<string> keys;
    for (auto i = 0; i < COUNT; i++) keys.push_back(to_string(i));

    // test all engines for all keys & values
    test_engine("blackhole", keys, "AAAAAAAAAAAAAAAA");
    test_engine("kvtree3", keys, "AAAAAAAAAAAAAAAA");
    test_engine("btree", keys, "AAAAAAAAAAAAAAAA");

    LOG("\nFinished!\n");
    return 0;
}
