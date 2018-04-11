require '../../pmemkv-ruby/lib/pmemkv/kv_engine'

def test_engine(engine, count)
  puts "\nTesting #{engine} engine..."
  kv = KVEngine.new(engine, '/dev/shm/pmemkv', 1024 * 1024 * 1024)

  puts "Putting #{count} sequential values"
  t1 = Time.now
  count.times do |i|
    kv.put(i.to_s, 'AAAAAAAAAAAAAAAA') # 16-char value
  end
  puts "   in #{Time.now - t1} sec"

  puts "Getting #{count} sequential values"
  t1 = Time.now
  failures = 0
  count.times do |i|
    failures += 1 if kv.get(i.to_s).nil?
  end
  puts "   in #{Time.now - t1} sec, failures=#{failures}"
end

count = 1000000
test_engine('kvtree2', count)
test_engine('blackhole', count)
puts "\nFinished!\n\n"
