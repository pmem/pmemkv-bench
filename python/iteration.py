from pmemkv import Database
import os
import time

count = 100000000
failures = count
path = r"/dev/shm/pmemkv"

def func(key = "", value = ""):
    global failures
    failures -= 1

def test_engine(engine, value):
    global count, path, failures

    print ("\nTesting {} engine for {} keys, value size is {}...".format(engine, count, len(value)))

    if os.path.isfile(path):
        os.remove(path)

    db = Database(engine, '{"path": \"' + str(path) + '\", "size": 1073741824, "force_create": 1}')
    print ("Put (sequential series)")
    t1 = time.time()
    for i in range(0, count):
        db.put(str(i), value)
    print ("   in "+ str(time.time() - t1) + " sec(s)")

    print ("All strings (one pass)")
    t1 = time.time()
    db.get_keys_strings(func)
    print ("   in " + str(time.time() - t1) + " sec(s), failures=" + str(failures))
    failures = count

    print ("All (one pass)")
    t1 = time.time()
    db.get_keys(func)
    print ("   in " + str(time.time() - t1) + " sec(s), failures=" + str(failures))
    failures = count

    print ("Each string (one pass)")
    t1 = time.time()
    db.get_all_string(func)
    print ("   in " + str(time.time() - t1) + " sec(s), failures=" + str(failures))
    failures = count

    print ("Each (one pass)")
    t1 = time.time()
    db.get_all(func)
    print ("   in "+  str(time.time() - t1) + " sec(s), failures=" + str(failures))
    failures = count

    db.stop()

test_engine(r"cmap", r"A" * 64)

print ("\nFinished!\n\n")
