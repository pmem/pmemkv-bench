require '../../pmemkv-ruby/lib/pmemkv/kv_engine'

def assert(condition)
  raise RuntimeError.new('Assert failed') unless condition
end

puts 'Opening datastore'
kv = KVEngine.new('kvtree3', '/dev/shm/pmemkv', 1073741824) # 1 GB pool

puts 'Putting new key'
kv.put('key1', 'value1')
assert kv.count == 1

puts 'Reading key back'
assert kv.get('key1').eql?('value1')

puts 'Iterating existing keys'
kv.put('key2', 'value2')
kv.put('key3', 'value3')
kv.each_string {|k, v| puts "  visited: #{k}"}

puts 'Removing existing key'
kv.remove('key1')
assert !kv.exists('key1')

puts 'Closing datastore'
kv.close