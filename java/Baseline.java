import io.pmem.pmemkv.KVEngine;

import java.io.File;
import java.util.concurrent.atomic.AtomicInteger;

public class Baseline {

    public final static String FILE = "/dev/shm/pmemkv";

    public static void test_engine(String engine, int count) {
        System.out.printf("%nTesting %s engine...%n", engine);
        (new File(FILE)).delete();
        KVEngine kv = new KVEngine(engine, FILE, 1024 * 1024 * 1024L);

        System.out.printf("Put for %d sequential values%n", count);
        long start = System.currentTimeMillis();
        for (int i = 1; i <= count; i++) {
            kv.put(Integer.toString(i).getBytes(), "AAAAAAAAAAAAAAAA".getBytes());
        }
        double elapsed = (System.currentTimeMillis() - start) / 1000.0;
        System.out.printf("  in %f sec%n", elapsed);

        System.out.printf("Get for %d sequential values%n", count);
        start = System.currentTimeMillis();
        int failures = 0;
        for (int i = 1; i <= count; i++) {
            byte[] result = kv.get(Integer.toString(i).getBytes());
            if (result == null || result.length == 0) failures++;
        }
        elapsed = (System.currentTimeMillis() - start) / 1000.0;
        System.out.printf("  in %f sec, failures=%d%n", elapsed, failures);

        System.out.printf("Each for %d values%n", count);
        start = System.currentTimeMillis();
        AtomicInteger callbacks = new AtomicInteger(0);
        kv.each((k, v) -> callbacks.incrementAndGet());
        elapsed = (System.currentTimeMillis() - start) / 1000.0;
        System.out.printf("  in %f sec, failures=%d%n", elapsed, count - callbacks.get());

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
