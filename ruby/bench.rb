require '../../pmemkv-ruby/lib/pmemkv/kv_engine'

def test_engine(engine, count)
  puts "\nTesting #{engine} engine..."
  kv = KVEngine.new(engine, '/dev/shm/pmemkv', 1024 * 1024 * 1024)

  puts "Put for #{count} sequential values"
  t1 = Time.now
  count.times do |i|
    kv.put(i.to_s, 'AAAAAAAAAAAAAAAA') # 16-char value
  end
  puts "   in #{Time.now - t1} sec"

  puts "Get for #{count} sequential values"
  t1 = Time.now
  failures = 0
  count.times do |i|
    failures += 1 if kv.get(i.to_s).nil?
  end
  puts "   in #{Time.now - t1} sec, failures=#{failures}"

  puts "Each for #{count} sequential values"
  t1 = Time.now
  failures = count
  kv.each {|k, v| failures -= 1}
  puts "   in #{Time.now - t1} sec, failures=#{failures}"

  puts "Exists for #{count} sequential values"
  t1 = Time.now
  failures = 0
  count.times do |i|
    failures += 1 unless kv.exists(i.to_s)
  end
  puts "   in #{Time.now - t1} sec, failures=#{failures}"

  kv.close();
end

count = 1000000
test_engine('blackhole', count)
test_engine('btree', count)
puts "\nFinished!\n\n"
