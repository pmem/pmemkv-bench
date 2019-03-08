#include <iostream>
#include <sys/time.h>
#include <vector>
#include "libpmemkv.h"

#define LOG(msg) std::cout << msg << "\n"

using namespace pmemkv;

static const int COUNT = 100000000;
static const string PATH = "/dev/shm/pmemkv";

static double current_seconds() {
    struct timeval tv;
    gettimeofday(&tv, NULL);
    return (tv.tv_sec) + (double) (tv.tv_usec) / 1000000;
}

struct CallbackContext {
    unsigned long failures;
};

void test_engine(const string engine, const string value) {
    LOG("\nTesting " << engine << " for " + to_string(COUNT) << " keys, value size is "
                     << value.length() << "...");
    std::remove(PATH.c_str());
    KVEngine* kv = KVEngine::Start(engine, "{\"path\":\"" + PATH + "\",\"size\":16106127360}");

    LOG("Put (sequential series)");
    auto started = current_seconds();
    for (int i = 0; i < COUNT; i++) {
        if (kv->Put(to_string(i), value) != OK) {
            std::cout << "Out of space at key " << to_string(i) << "\n";
            exit(-42);
        }
    }
    LOG("   in " << current_seconds() - started << " sec");

    LOG("All (one pass)");
    CallbackContext cxt = {COUNT};
    auto cba = [](void* context, int keybytes, const char* key) {
        ((CallbackContext*) context)->failures--;
    };
    started = current_seconds();
    kv->All(&cxt, cba);
    LOG("   in " << current_seconds() - started << " sec, failures=" + to_string(cxt.failures));

    LOG("Each (one pass)");
    cxt = {COUNT};
    auto cb = [](void* context, int keybytes, const char* key, int valuebytes, const char* value) {
        ((CallbackContext*) context)->failures--;
    };
    started = current_seconds();
    kv->Each(&cxt, cb);
    LOG("   in " << current_seconds() - started << " sec, failures=" + to_string(cxt.failures));

    delete kv;
}

int main() {
    test_engine("tree3", std::string(64, 'A'));
    LOG("\nFinished!\n");
    return 0;
}
