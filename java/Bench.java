import io.pmem.pmemkv.KVEngine;

public class Bench {

    public static void test_engine(String engine, int count) {
        System.out.printf("%nTesting %s engine...%n", engine);
        KVEngine kv = new KVEngine(engine, "/dev/shm/pmemkv", 1024 * 1024 * 1024);

        System.out.printf("Putting %d sequential values%n", count);
        long start = System.currentTimeMillis();
        for (int i = 1; i <= count; i++) {
            kv.put(Integer.toString(i), "AAAAAAAAAAAAAAAA"); // 16-char value
        }
        double elapsed = (System.currentTimeMillis() - start) / 1000.0;
        System.out.printf("  in %f sec%n", elapsed);

        System.out.printf("Getting %d sequential values%n", count);
        start = System.currentTimeMillis();
        int failures = 0;
        for (int i = 1; i <= count; i++) {
            String result = kv.get(Integer.toString(i));
            if (result == null) failures++;
        }
        elapsed = (System.currentTimeMillis() - start) / 1000.0;
        System.out.printf("  in %f sec, failures=%d%n", elapsed, failures);
    }

    public static void main(String[] args) {
        int count = 1000000;
        test_engine("kvtree", count);
        test_engine("blackhole", count);
        System.out.printf("%nFinished!%n%n");
    }
}