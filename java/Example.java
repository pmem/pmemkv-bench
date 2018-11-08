import io.pmem.pmemkv.KVEngine;

public class Example {
    public static void main(String[] args) {
        System.out.println("Starting engine");
        KVEngine kv = new KVEngine("kvtree3", "{\"path\":\"/dev/shm/pmemkv\"}");

        System.out.println("Putting new key");
        kv.put("key1", "value1");
        assert kv.count() == 1;

        System.out.println("Reading key back");
        assert kv.get("key1").equals("value1");

        System.out.println("Iterating existing keys");
        kv.put("key2", "value2");
        kv.put("key3", "value3");
        kv.all((String k) -> System.out.println("  visited: " + k));

        System.out.println("Removing existing key");
        kv.remove("key1");
        assert !kv.exists("key1");

        System.out.println("Stopping engine");
        kv.stop();
    }
}
