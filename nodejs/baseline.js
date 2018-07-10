const fs = require('fs');
const KVEngine = require('../../pmemkv-nodejs/lib/kv_engine');

const COUNT = 1000000;
const FILE = '/dev/shm/pmemkv';

function test_engine(engine, value) {
    console.log(`\nTesting ${engine} engine for ${COUNT} keys, value size is ${value.length}...`);
    if (fs.existsSync(FILE)) fs.unlinkSync(FILE);
    const kv = new KVEngine(engine, FILE, 1024 * 1024 * 1024);

    console.log(`Put (sequential)`);
    console.time("  in");
    for (let i = 1; i <= COUNT; i++) {
        kv.put(i.toString(), value);
    }
    console.timeEnd("  in");

    console.log(`Get (sequential)`);
    let failures = 0;
    console.time("  in");
    for (let i = 1; i <= COUNT; i++) {
        const result = kv.get(i.toString());
        if (typeof result === 'undefined' || result === null) failures++;
    }
    console.timeEnd("  in");
    console.log(`  failures: ${failures}`);

    console.log(`Exists (sequential)`);
    failures = 0;
    console.time("  in");
    for (let i = 1; i <= COUNT; i++) {
        if (!kv.exists(i.toString())) failures++;
    }
    console.timeEnd("  in");
    console.log(`  failures: ${failures}`);

    console.log(`Each (natural)`);
    failures = COUNT;
    console.time("  in");
    kv.each(
        function (k, v) {
            failures--;
        }
    );
    console.timeEnd("  in");
    console.log(`  failures: ${failures}`);

    kv.close();
}

// test all engines for all keys & values
test_engine('blackhole', 'AAAAAAAAAAAAAAAA');
test_engine('btree', 'AAAAAAAAAAAAAAAA');

console.log('\nFinished!\n\n');
