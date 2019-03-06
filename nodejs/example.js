const KVEngine = require('../../pmemkv-nodejs/lib/kv_engine');

function assert(condition) {
    if (!condition) throw new Error('Assert failed');
}

console.log('Starting engine');
const kv = new KVEngine('vsmap', '{"path":"/dev/shm/"}');

console.log('Putting new key');
kv.put('key1', 'value1');
assert(kv.count === 1);

console.log('Reading key back');
assert(kv.get('key1') === 'value1');

console.log('Iterating existing keys');
kv.put('key2', 'value2');
kv.put('key3', 'value3');
kv.all((k) => console.log(`  visited: ${k}`));

console.log('Removing existing key');
kv.remove('key1');
assert(!kv.exists('key1'));

console.log('Stopping engine');
kv.stop();
