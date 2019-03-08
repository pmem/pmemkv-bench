require '../../pmemkv-ruby/lib/pmemkv/kv_engine'

COUNT = 1000000
PATH = '/dev/shm/pmemkv'

def test_engine(engine, value)
  puts "\nTesting #{engine} engine for #{COUNT} keys, value size is #{value.length}..."
  File.delete(PATH) if File.exist?(PATH)
  kv = KVEngine.new(engine, "{\"path\":\"#{PATH}\"}")

  puts "Put (sequential series)"
  t1 = Time.now
  COUNT.times do |i|
    kv.put(i.to_s, value)
  end
  puts "   in #{Time.now - t1} sec"

  puts "Get (sequential series)"
  failures = 0
  t1 = Time.now
  COUNT.times do |i|
    failures += 1 if kv.get(i.to_s).nil?
  end
  puts "   in #{Time.now - t1} sec, failures=#{failures}"

  puts "Exists (sequential series)"
  failures = 0
  t1 = Time.now
  COUNT.times do |i|
    failures += 1 unless kv.exists(i.to_s)
  end
  puts "   in #{Time.now - t1} sec, failures=#{failures}"

  puts "All (one pass)"
  failures = COUNT
  t1 = Time.now
  kv.all {|k| failures -= 1}
  puts "   in #{Time.now - t1} sec, failures=#{failures}"

  puts "Each (one pass)"
  failures = COUNT
  t1 = Time.now
  kv.each {|k, v| failures -= 1}
  puts "   in #{Time.now - t1} sec, failures=#{failures}"

  kv.stop
end

# test all engines for all keys & values
test_engine('blackhole', 'AAAAAAAAAAAAAAAA')
test_engine('tree3', 'AAAAAAAAAAAAAAAA')
test_engine('tree3', 'A' * 200)
test_engine('tree3', 'A' * 800)

puts "\nFinished!\n\n"
