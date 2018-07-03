import io.pmem.pmemkv.KVEngine;

import java.io.File;

public class Bench {

    public static void test_engine(String engine, int count) {
        System.out.printf("%nTesting %s engine...%n", engine);
        (new File("/dev/shm/pmemkv")).delete();
        KVEngine kv = new KVEngine(engine, "/dev/shm/pmemkv", 1024 * 1024 * 1024L);

        System.out.printf("Put for %d sequential values%n", count);
        long start = System.currentTimeMillis();
        for (int i = 1; i <= count; i++) {
            kv.put(Integer.toString(i).getBytes(), "AAAAAAAAAAAAAAAA".getBytes());
        }
        double elapsed = (System.currentTimeMillis() - start) / 1000.0;
        System.out.printf("  in %f sec%n", elapsed);

        System.out.printf("Get for %d sequential values as byte[]%n", count);
        start = System.currentTimeMillis();
        int failures = 0;
        for (int i = 1; i <= count; i++) {
            byte[] result = kv.get(Integer.toString(i).getBytes());
            if (result == null || result.length == 0) failures++;
        }
        elapsed = (System.currentTimeMillis() - start) / 1000.0;
        System.out.printf("  in %f sec, failures=%d%n", elapsed, failures);

        System.out.printf("Each for %d values as byte[]%n", count);
        start = System.currentTimeMillis();
        StringBuilder x = new StringBuilder();
        kv.each((k, v) -> x.append('x'));
        elapsed = (System.currentTimeMillis() - start) / 1000.0;
        System.out.printf("  in %f sec, failures=%d%n", elapsed, count - x.length());

        System.out.printf("Exists for %d sequential values%n", count);
        start = System.currentTimeMillis();
        failures = 0;
        for (int i = 1; i <= count; i++) {
            if (!kv.exists(Integer.toString(i).getBytes())) failures++;
        }
        elapsed = (System.currentTimeMillis() - start) / 1000.0;
        System.out.printf("  in %f sec, failures=%d%n", elapsed, failures);

        kv.close();
    }

    public static void main(String[] args) {
        int count = 1000000;
        test_engine("blackhole", count);
        test_engine("btree", count);
        System.out.printf("%nFinished!%n%n");
    }
}
