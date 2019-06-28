require '../../pmemkv-ruby/lib/pmemkv/database'

def assert(condition)
  raise RuntimeError.new('Assert failed') unless condition
end

puts 'Starting engine'
db = Database.new('vsmap', "{\"path\":\"/dev/shm\",\"size\":1073741824}")

puts 'Putting new key'
db.put('key1', 'value1')
assert db.count_all == 1

puts 'Reading key back'
assert db.get('key1').eql?('value1')

puts 'Iterating existing keys'
db.put('key2', 'value2')
db.put('key3', 'value3')
db.get_keys {|k| puts "  visited: #{k}"}

puts 'Removing existing key'
db.remove('key1')
assert !db.exists('key1')

puts 'Stopping engine'
db.stop
