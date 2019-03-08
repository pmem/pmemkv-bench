import io.pmem.pmemkv.KVEngine;

import java.io.File;
import java.util.concurrent.atomic.AtomicInteger;

public class Baseline {

    public final static int COUNT = 1000000;
    public final static String PATH = "/dev/shm/pmemkv";

    public static void test_engine(String engine, byte[][] keys, byte[] value) {
        System.out.printf("%nTesting %s engine for %s keys, value size is %s...%n", engine, COUNT, value.length);
        (new File(PATH)).delete();
        KVEngine kv = new KVEngine(engine, "{\"path\":\"" + PATH + "\"}");

        System.out.printf("Put (sequential series)%n");
        long start = System.currentTimeMillis();
        for (byte[] k : keys) kv.put(k, value);
        double elapsed = (System.currentTimeMillis() - start) / 1000.0;
        System.out.printf("  in %f sec%n", elapsed);

        System.out.printf("Get (sequential series)%n");
        int failures = 0;
        start = System.currentTimeMillis();
        for (byte[] k : keys) {
            byte[] result = kv.get(k);
            if (result == null || result.length == 0) failures++;
        }
        elapsed = (System.currentTimeMillis() - start) / 1000.0;
        System.out.printf("  in %f sec, failures=%d%n", elapsed, failures);

        System.out.printf("Exists (sequential series)%n");
        failures = 0;
        start = System.currentTimeMillis();
        for (byte[] k : keys) if (!kv.exists(k)) failures++;
        elapsed = (System.currentTimeMillis() - start) / 1000.0;
        System.out.printf("  in %f sec, failures=%d%n", elapsed, failures);

        System.out.printf("All (one pass)%n");
        AtomicInteger callbacks = new AtomicInteger(0);
        start = System.currentTimeMillis();
        kv.all((byte[] k) -> callbacks.incrementAndGet());
        elapsed = (System.currentTimeMillis() - start) / 1000.0;
        System.out.printf("  in %f sec, failures=%d%n", elapsed, keys.length - callbacks.get());

        System.out.printf("Each (one pass)%n");
        callbacks.set(0);
        start = System.currentTimeMillis();
        kv.each((byte[] k, byte[] v) -> callbacks.incrementAndGet());
        elapsed = (System.currentTimeMillis() - start) / 1000.0;
        System.out.printf("  in %f sec, failures=%d%n", elapsed, keys.length - callbacks.get());

        kv.stop();
    }

    public static void main(String[] args) {
        // format all keys in advance
        byte[][] keys = new byte[COUNT][];
        for (int i = 0; i < COUNT; i++) {
            keys[i] = Integer.toString(i).getBytes();
        }

        // test all engines for all keys & values
        test_engine("blackhole", keys, "AAAAAAAAAAAAAAAA".getBytes());
        test_engine("tree3", keys, "AAAAAAAAAAAAAAAA".getBytes());
        test_engine("tree3", keys, (new String(new char[200]).replace("\0", "A")).getBytes());
        test_engine("tree3", keys, (new String(new char[800]).replace("\0", "A")).getBytes());

        System.out.printf("%nFinished!%n%n");
    }

}
