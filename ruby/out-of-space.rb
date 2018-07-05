require '../../pmemkv-ruby/lib/pmemkv/kv_engine'

def test_engine(engine, count)
  puts "\nTesting #{engine} engine..."
  kv = KVEngine.new(engine, '/dev/shm/pmemkv', 1024 * 1024 * 1104)

  puts "Putting #{count} sequential values"
  t1 = Time.now
  count.times do |i|
    kv.put(i.to_s, "#{i.to_s}!")
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

count = 8012298
test_engine('kvtree', count)
test_engine('blackhole', count)
puts "\nFinished!\n\n"
