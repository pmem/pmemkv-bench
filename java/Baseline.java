import io.pmem.pmemkv.KVEngine;

import java.io.File;
import java.util.concurrent.atomic.AtomicInteger;

public class Baseline {

    public final static int COUNT = 1000000;
    public final static String FILE = "/dev/shm/pmemkv";

    public static void test_engine(String engine, byte[][] keys, byte[] value) {
        System.out.printf("%nTesting %s engine for %s keys, value size is %s...%n",
                engine, COUNT, value.length);
        (new File(FILE)).delete();
        KVEngine kv = new KVEngine(engine, FILE, 1024 * 1024 * 1024L);

        // Test put operation
        System.out.printf("Put (sequential)%n");
        long start = System.currentTimeMillis();
        for (byte[] k : keys) kv.put(k, value);
        double elapsed = (System.currentTimeMillis() - start) / 1000.0;
        System.out.printf("  in %f sec%n", elapsed);

        // Test get operation
        System.out.printf("Get (sequential)%n");
        int failures = 0;
        start = System.currentTimeMillis();
        for (byte[] k : keys) {
            byte[] result = kv.get(k);
            if (result == null || result.length == 0) failures++;
        }
        elapsed = (System.currentTimeMillis() - start) / 1000.0;
        System.out.printf("  in %f sec, failures=%d%n", elapsed, failures);

        // Test exists operation
        System.out.printf("Exists (sequential)%n");
        failures = 0;
        start = System.currentTimeMillis();
        for (byte[] k : keys) if (!kv.exists(k)) failures++;
        elapsed = (System.currentTimeMillis() - start) / 1000.0;
        System.out.printf("  in %f sec, failures=%d%n", elapsed, failures);

        // Test each operation
        System.out.printf("Each (natural)%n");
        AtomicInteger callbacks = new AtomicInteger(0);
        start = System.currentTimeMillis();
        kv.each((k, v) -> callbacks.incrementAndGet());
        elapsed = (System.currentTimeMillis() - start) / 1000.0;
        System.out.printf("  in %f sec, failures=%d%n", elapsed, keys.length - callbacks.get());

        kv.close();
    }

    public static void main(String[] args) {
        // format all keys in advance
        byte[][] keys = new byte[COUNT][];
        for (int i = 0; i < COUNT; i++) {
            keys[i] = Integer.toString(i).getBytes();
        }

        // test all engines for all keys & values
        test_engine("blackhole", keys, "AAAAAAAAAAAAAAAA".getBytes());
        test_engine("kvtree2", keys, "AAAAAAAAAAAAAAAA".getBytes());
        test_engine("btree", keys, "AAAAAAAAAAAAAAAA".getBytes());

        System.out.printf("%nFinished!%n%n");
    }

}
