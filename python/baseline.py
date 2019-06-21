from pmemkv import Database
import os
import time

count = 1000000
failures = count
path = r"/dev/shm/pmemkv"

def func(key = "", value = ""):
    global failures
    failures -= 1

def test_engine(engine, value):
    global count, path, failures

    print ("\nTesting " + engine + " engine for " + str(count) + " keys, value size is " + str(len(value)) + "...")
    if os.path.isfile(path):
        os.remove(path)

    db = Database(engine, "{\"path\":\""+ path +"\"}")
    print ("Put (sequential series)")
    t1 = time.time()
    for i in range(0, count):
        db.put(str(i), value)
    print ("   in "+ str(time.time() - t1) + " sec(s)")

    print ("Get (sequential series)")
    failures = 0
    t1 = time.time()
    for i in range(0, count):
        if db.get(str(i)) == None:
            failures += 1
    print ("   in " + str(time.time() - t1) + " sec(s), failures= " + str(failures))

    print ("Exists (sequential series)")
    failures = 0
    t1 = time.time()
    for i in range(0, count):
        if not db.exists(str(i)):
            failures += 1
    print ("   in " + str(time.time() - t1) + " sec(s), failures=" + str(failures))

    print ("All (one pass)")
    failures = count
    t1 = time.time()
    db.all(func)
    print ("   in " + str(time.time() - t1) + " sec(s), failures=" + str(failures))

    print ("Each (one pass)")
    failures = count
    t1 = time.time()
    db.each(func)
    print ("   in "+  str(time.time() - t1) + " sec(s), failures=" + str(failures))

    db.stop()

# test all engines for all keys & values
test_engine(r"blackhole", r"AAAAAAAAAAAAAAAA")
test_engine(r"tree3", r"AAAAAAAAAAAAAAAA")
test_engine(r"tree3", r"A" * 200)
test_engine(r"tree3", r"A" * 800)

print ("\nFinished!\n\n")
