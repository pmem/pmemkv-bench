const fs = require('fs');
const KVEngine = require('../../pmemkv-nodejs/lib/kv_engine');

const COUNT = 1000000;
const FILE = '/dev/shm/pmemkv';

function test_engine(engine, value) {
    console.log(`\nTesting ${engine} engine for ${COUNT} keys, value size is ${value.length}...`);
    if (fs.existsSync(FILE)) fs.unlinkSync(FILE);
    const kv = new KVEngine(engine, FILE, 1024 * 1024 * 1024);

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

    console.log(`Each (one pass)`);
    failures = COUNT;
    console.time("  in");
    kv.each(() => failures--);
    console.timeEnd("  in");
    console.log(`  failures: ${failures}`);

    console.log(`EachLike (one pass, all keys match)`);
    failures = COUNT;
    console.time("  in");
    kv.each_like('.*', () => failures--);
    console.timeEnd("  in");
    console.log(`  failures: ${failures}`);

    console.log(`EachLike (one pass, one key matches)`);
    failures = 1;
    console.time("  in");
    kv.each_like('1234', () => failures--);
    console.timeEnd("  in");
    console.log(`  failures: ${failures}`);

    kv.close();
}

// test all engines for all keys & values
test_engine('blackhole', 'AAAAAAAAAAAAAAAA');
test_engine('kvtree3', 'AAAAAAAAAAAAAAAA');
test_engine('btree', 'AAAAAAAAAAAAAAAA');

console.log('\nFinished!\n\n');
