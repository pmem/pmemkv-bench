const KVEngine = require('../../pmemkv-nodejs/lib/kv_engine');

function test_engine(engine, count) {
    console.log(`\nTesting ${engine} engine...`);
    const kv = new KVEngine(engine, '/dev/shm/pmemkv', 1024 * 1024 * 1024);

    console.log(`Put for ${count} sequential values`);
    console.time("  in");
    for (let i = 1; i <= count; i++) {
        kv.put(i.toString(), 'AAAAAAAAAAAAAAAA');  // 16-char value
    }
    console.timeEnd("  in");

    console.log(`Get for ${count} sequential values`);
    console.time("  in");
    let failures = 0;
    for (let i = 1; i <= count; i++) {
        const result = kv.get(i.toString());
        if (typeof result === 'undefined' || result === null) failures++;
    }
    console.timeEnd("  in");
    console.log(`  failures: ${failures}`);

    console.log(`Each for ${count} sequential values`);
    console.time("  in");
    failures = count;
    kv.each(
        function (k, v) {
            failures--;
        }
    );
    console.timeEnd("  in");
    console.log(`  failures: ${failures}`);

    console.log(`Exists for ${count} sequential values`);
    console.time("  in");
    failures = 0;
    for (let i = 1; i <= count; i++) {
        if (!kv.exists(i.toString())) failures++;
    }
    console.timeEnd("  in");
    console.log(`  failures: ${failures}`);
}

const count = 1000000;
test_engine('blackhole', count);
test_engine('btree', count);
console.log('\nFinished!\n\n');
