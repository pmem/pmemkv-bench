from pmemkv import Database

print ("Starting engine")
db = Database(r"vsmap", "{\"path\":\"/dev/shm/\"}")

print ("Put new key")
db.put(r"key1", r"value1")
assert db.count() == 1

print ("Reading key back")
assert db.get(r"key1") == r"value1"

print ("Iterating existing keys")
db.put(r"key2", r"value2")
db.put(r"key3", r"value3")
db.all_strings(lambda k: print ("  visited: {}".format(k.decode())))

print ("Removing existing key")
db.remove(r"key1")
assert not db.exists(r"key1")

print ("Stopping engine")
db.stop()
