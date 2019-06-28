const Database = require('../../pmemkv-nodejs/lib/database');

function assert(condition) {
    if (!condition) throw new Error('Assert failed');
}

console.log('Starting engine');
const db = new Database('vsmap', '{"path":"/dev/shm", "size":1073741824}');

console.log('Putting new key');
db.put('key1', 'value1');
assert(db.count_all === 1);

console.log('Reading key back');
assert(db.get('key1') === 'value1');

console.log('Iterating existing keys');
db.put('key2', 'value2');
db.put('key3', 'value3');
db.get_keys((k) => console.log(`  visited: ${k}`));

console.log('Removing existing key');
db.remove('key1');
assert(!db.exists('key1'));

console.log('Stopping engine');
db.stop();
