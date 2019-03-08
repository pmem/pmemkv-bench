const fs = require('fs');
const KVEngine = require('../../pmemkv-nodejs/lib/kv_engine');

const COUNT = 1000000;
const PATH = '/dev/shm/pmemkv';

function test_engine(engine, value) {
    console.log(`\nTesting ${engine} engine for ${COUNT} keys, value size is ${value.length}...`);
    if (fs.existsSync(PATH)) fs.unlinkSync(PATH);
    const kv = new KVEngine(engine, `{"path":"${PATH}"}`);

    console.log(`Put (sequential series)`);
    console.time("  in");
    for (let i = 1; i <= COUNT; i++) {
        kv.put(i.toString(), value);
    }
    console.timeEnd("  in");

    console.log(`Get (sequential series)`);
    let failures = 0;
    console.time("  in");
    for (let i = 1; i <= COUNT; i++) {
        const result = kv.get(i.toString());
        if (typeof result === 'undefined' || result === null) failures++;
    }
    console.timeEnd("  in");
    console.log(`  failures: ${failures}`);

    console.log(`Exists (sequential series)`);
    failures = 0;
    console.time("  in");
    for (let i = 1; i <= COUNT; i++) {
        if (!kv.exists(i.toString())) failures++;
    }
    console.timeEnd("  in");
    console.log(`  failures: ${failures}`);

    console.log(`All (one pass)`);
    failures = COUNT;
    console.time("  in");
    kv.all(() => failures--);
    console.timeEnd("  in");
    console.log(`  failures: ${failures}`);

    console.log(`Each (one pass)`);
    failures = COUNT;
    console.time("  in");
    kv.each(() => failures--);
    console.timeEnd("  in");
    console.log(`  failures: ${failures}`);

    kv.stop();
}

// test all engines for all keys & values
test_engine('blackhole', 'AAAAAAAAAAAAAAAA');
test_engine('tree3', 'AAAAAAAAAAAAAAAA');
test_engine('tree3', 'A'.repeat(200));
test_engine('tree3', 'A'.repeat(800));

console.log('\nFinished!\n\n');
