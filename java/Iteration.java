import io.pmem.pmemkv.KVEngine;

import java.io.File;
import java.nio.ByteBuffer;
import java.util.concurrent.atomic.AtomicInteger;

public class Iteration {

    public final static int COUNT = 100000000;
    public final static String PATH = "/dev/shm/pmemkv";

    public static void test_engine(String engine, byte[] value) {
        System.out.printf("%nTesting %s engine for %s keys, value size is %s...%n", engine, COUNT, value.length);
        (new File(PATH)).delete();
        KVEngine kv = new KVEngine(engine, "{\"path\":\"" + PATH + "\",\"size\":16106127360}");

        System.out.printf("Put (sequential series)%n");
        long start = System.currentTimeMillis();
        for (int i = 0; i < COUNT; i++) kv.put(Integer.toString(i).getBytes(), value);
        double elapsed = (System.currentTimeMillis() - start) / 1000.0;
        System.out.printf("  in %f sec%n", elapsed);

        System.out.printf("All buffers (one pass)%n");
        AtomicInteger callbacks = new AtomicInteger(0);
        start = System.currentTimeMillis();
        kv.all((ByteBuffer key) -> callbacks.incrementAndGet());
        elapsed = (System.currentTimeMillis() - start) / 1000.0;
        System.out.printf("  in %f sec, failures=%d%n", elapsed, COUNT - callbacks.get());

        System.out.printf("Each buffer (one pass)%n");
        callbacks.set(0);
        start = System.currentTimeMillis();
        kv.each((ByteBuffer kbuf, ByteBuffer vbuf) -> callbacks.incrementAndGet());
        elapsed = (System.currentTimeMillis() - start) / 1000.0;
        System.out.printf("  in %f sec, failures=%d%n", elapsed, COUNT - callbacks.get());

        System.out.printf("All byte arrays (one pass)%n");
        callbacks.set(0);
        start = System.currentTimeMillis();
        kv.all((String key) -> callbacks.incrementAndGet());
        elapsed = (System.currentTimeMillis() - start) / 1000.0;
        System.out.printf("  in %f sec, failures=%d%n", elapsed, COUNT - callbacks.get());

        System.out.printf("Each byte array (one pass)%n");
        callbacks.set(0);
        start = System.currentTimeMillis();
        kv.each((byte[] k, byte[] v) -> callbacks.incrementAndGet());
        elapsed = (System.currentTimeMillis() - start) / 1000.0;
        System.out.printf("  in %f sec, failures=%d%n", elapsed, COUNT - callbacks.get());

        System.out.printf("All strings (one pass)%n");
        callbacks.set(0);
        start = System.currentTimeMillis();
        kv.all((String kstr) -> callbacks.incrementAndGet());
        elapsed = (System.currentTimeMillis() - start) / 1000.0;
        System.out.printf("  in %f sec, failures=%d%n", elapsed, COUNT - callbacks.get());

        System.out.printf("Each string (one pass)%n");
        callbacks.set(0);
        start = System.currentTimeMillis();
        kv.each((String kstr, String vstr) -> callbacks.incrementAndGet());
        elapsed = (System.currentTimeMillis() - start) / 1000.0;
        System.out.printf("  in %f sec, failures=%d%n", elapsed, COUNT - callbacks.get());

        kv.stop();
    }

    public static void main(String[] args) {
        test_engine("tree3", (new String(new char[64]).replace("\0", "A")).getBytes());
        System.out.printf("%nFinished!%n%n");
    }

}
