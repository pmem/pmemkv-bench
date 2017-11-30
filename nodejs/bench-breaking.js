const KVEngine = require('../../pmemkv-nodejs/lib/kv_engine');

function test_engine(engine, count) {
    console.log(`\nTesting ${engine} engine...`);
    const kv = new KVEngine(engine, '/dev/shm/pmemkv', 1024 * 1024 * 1104);

    console.log(`Putting ${count} sequential values`);
    console.time("  in");
    for (let i = 1; i <= count; i++) {
        kv.put(i.toString(), `${i.toString()}!`);
    }
    console.timeEnd("  in");

    console.log(`Getting ${count} sequential values`);
    console.time("  in");
    let failures = 0;
    for (let i = 1; i <= count; i++) {
        const result = kv.get(i.toString());
        if (typeof result === 'undefined' || result === null) failures++;
    }
    console.timeEnd("  in");
    console.log(`  failures: ${failures}`);
}

const count = 6012298;
test_engine('kvtree', count);
test_engine('blackhole', count);
console.log('\nFinished!\n\n');
