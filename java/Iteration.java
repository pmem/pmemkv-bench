import io.pmem.pmemkv.KVEngine;

import java.io.File;
import java.util.concurrent.atomic.AtomicInteger;

public class Iteration {

    public final static long SIZE = 15 * 1024 * 1024 * 1024L;
    public final static int COUNT = 100000000;
    public final static String FILE = "/dev/shm/pmemkv";

    public static void test_engine(String engine, byte[] value) {
        System.out.printf("%nTesting %s engine for %s keys, value size is %s...%n", engine, COUNT, value.length);
        (new File(FILE)).delete();
        KVEngine kv = new KVEngine(engine, FILE, SIZE);

        System.out.printf("Put (sequential series)%n");
        long start = System.currentTimeMillis();
        for (int i = 0; i < COUNT; i++) kv.put(Integer.toString(i).getBytes(), value);
        double elapsed = (System.currentTimeMillis() - start) / 1000.0;
        System.out.printf("  in %f sec%n", elapsed);

        System.out.printf("All (one pass)%n");
        AtomicInteger callbacks = new AtomicInteger(0);
        start = System.currentTimeMillis();
        kv.all((k) -> callbacks.incrementAndGet());
        elapsed = (System.currentTimeMillis() - start) / 1000.0;
        System.out.printf("  in %f sec, failures=%d%n", elapsed, COUNT - callbacks.get());

        System.out.printf("Each (one pass)%n");
        callbacks.set(0);
        start = System.currentTimeMillis();
        kv.each((k, v) -> callbacks.incrementAndGet());
        elapsed = (System.currentTimeMillis() - start) / 1000.0;
        System.out.printf("  in %f sec, failures=%d%n", elapsed, COUNT - callbacks.get());

        kv.close();
    }

    public static void main(String[] args) {
        test_engine("kvtree3", (new String(new char[64]).replace("\0", "A")).getBytes());
        System.out.printf("%nFinished!%n%n");
    }

}
